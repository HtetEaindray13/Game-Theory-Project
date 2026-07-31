import settings
from agents.animal import Animal


class WildAnimal(Animal):
    def __init__(self, species, x, y, rng):
        profile = settings.SPECIES_PROFILES[species]
        strategy = {
            "Lion": "Pride hunter",
            "Crocodile": "Water ambush",
            "Mouse": "Burrow and forage",
            "Snake": "Venom ambush",
            "Buffalo": "Herd defense",
            "Zebra": "Herd vigilance",
            "Elephant": "Protective giant",
        }[species]
        super().__init__(species, x, y, strategy, rng)
        self.energy = rng.uniform(profile.max_energy * 0.58, profile.max_energy)
        self.max_energy = profile.max_energy
        self.max_age = profile.max_age
        self.vision_range = profile.vision
        self.reproduction_cooldown = 999999

    @property
    def profile(self):
        return settings.SPECIES_PROFILES[self.species]

    def decide(self, sim) -> None:
        threat, threat_distance = sim.nearest_threat(self)
        prey, prey_distance = sim.nearest_prey(self)
        terrain = sim.world.terrain[self.y][self.x]
        hunger = 1 - self.energy / self.max_energy

        if threat and threat_distance <= max(2, self.vision_range // 2):
            self.current_action = "Flee danger"
            self.target = threat.pos
            self.last_decision_reason = f"A stronger {threat.species.lower()} is {threat_distance} tiles away."
        elif (
            self.profile.role in {"predator", "ambush"}
            and prey
            and hunger > (0.36 if self.species == "Crocodile" else 0.26)
        ):
            self.current_action = "Ambush prey" if self.species in {"Snake", "Crocodile"} else "Hunt prey"
            self.target = prey.pos
            self.last_decision_reason = f"Tracking {prey.species.lower()} at range {prey_distance}."
        elif self.profile.role == "herbivore" and sim.world.grass_amount(self.x, self.y) >= 1 and hunger > 0.18:
            self.current_action = "Graze"
            self.target = self.pos
            self.last_decision_reason = "Food is available on this tile."
        elif self.profile.role == "herbivore":
            grass, distance = sim.world.nearest_tile(
                self.pos,
                lambda x, y: sim.world.grass_amount(x, y) >= 1,
                self.vision_range,
            )
            self.current_action = "Forage" if grass else "Stay with herd"
            self.target = grass
            self.last_decision_reason = f"Searching for grass within {self.vision_range} tiles."
        elif terrain not in self.profile.habitat:
            self.current_action = "Return to habitat"
            self.target = sim.nearest_habitat_tile(self)
            self.last_decision_reason = "Moving back toward preferred habitat."
        elif self.energy < self.max_energy * 0.35:
            self.current_action = "Rest"
            self.target = None
            self.last_decision_reason = "Conserving energy."
        else:
            self.current_action = "Rest" if self.profile.role in {"predator", "ambush"} else "Patrol"
            self.target = None
            self.last_decision_reason = "Satiated animals conserve energy instead of hunting."
        self.last_action_scores = {self.current_action: 100.0}

    def act(self, sim) -> None:
        if self.stunned_ticks > 0:
            self.current_action = "Stunned"
            self.lifecycle(self.profile.metabolism)
            return
        if self.slowed_ticks > 0 and sim.tick % 2:
            self.current_action = "Slowed by venom"
            self.lifecycle(self.profile.metabolism)
            return

        action = self.current_action
        if action == "Flee danger":
            self.move_to(sim.step_away_for(self, self.target), self.profile.walk_cost * 1.25)
        elif action in {"Hunt prey", "Ambush prey"}:
            prey, distance = sim.nearest_prey(self)
            if prey and distance <= 1:
                sim.try_attack(self, prey)
            elif prey:
                self.move_to(sim.step_toward_for(self, prey.pos), self.profile.walk_cost * 1.25)
            else:
                self.move_to(sim.random_neighbor(self), self.profile.walk_cost)
        elif action == "Graze":
            amount = 0.7 if self.species == "Mouse" else 1.5
            if self.species in {"Buffalo", "Elephant"}:
                amount = 2.2
            eaten = sim.world.eat_grass(self.x, self.y, amount)
            self.food_eaten += eaten
            self.gain_energy(eaten * self.profile.food_gain)
        elif action in {"Forage", "Return to habitat"}:
            self.move_to(sim.step_toward_for(self, self.target), self.profile.walk_cost)
        elif action == "Rest":
            self.gain_energy(0.8)
        else:
            self.move_to(sim.random_neighbor(self), self.profile.walk_cost * 0.55)
        self.lifecycle(self.profile.metabolism)
