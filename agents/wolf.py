import settings
from agents.animal import Animal
from ai import strategies, utility_ai


class Wolf(Animal):
    def __init__(self, x, y, rng, strategy: str | None = None):
        cfg = settings.WOLF
        super().__init__("Wolf", x, y, strategy or strategies.random_wolf_strategy(rng), rng)
        self.energy = rng.uniform(84, cfg.max_energy)
        self.max_energy = cfg.max_energy
        self.max_age = cfg.max_age
        self.speed = cfg.speed
        self.vision_range = cfg.vision_range
        self.reproduction_cooldown = rng.randint(25, cfg.reproduce_cooldown)

    def decide(self, sim) -> None:
        obs = sim.observe(self)
        scores, reason = utility_ai.wolf_scores(self, obs, sim.world, sim)
        self.last_action_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
        self.current_action = max(scores, key=scores.get)
        self.last_decision_reason = reason
        self.target = obs.get("nearest_rabbit") or obs.get("prey_hotspot")

    def act(self, sim) -> None:
        cfg = settings.WOLF
        if self.stunned_ticks > 0:
            self.current_action = "Stunned"
            self.lifecycle(cfg.metabolism)
            return
        if self.slowed_ticks > 0 and sim.tick % 2:
            self.current_action = "Slowed by venom"
            self.lifecycle(cfg.metabolism)
            return
        obs = sim.observe(self)
        action = self.current_action
        if action == "Hunt rabbit":
            adjacent = sim.adjacent_attack_target(self)
            prey, _ = sim.nearest_prey(self)
            prey = adjacent if adjacent and sim.is_predator_of(self, adjacent) else prey
            if prey and abs(prey.x - self.x) + abs(prey.y - self.y) <= 1:
                if prey.species == "Rabbit":
                    sim.try_hunt(self, prey)
                else:
                    sim.try_attack(self, prey)
            elif prey:
                self.move_to(sim.step_toward_for(self, prey.pos), cfg.chase_cost)
            else:
                self.move_to(sim.random_neighbor(self), cfg.walk_cost)
        elif action == "Chase rabbit":
            prey, _ = sim.nearest_prey(self)
            self.move_to(sim.step_toward_for(self, prey.pos if prey else None), cfg.chase_cost)
        elif action == "Move toward prey-rich territory":
            self.move_to(sim.world.step_toward(self.pos, obs["prey_hotspot"]), cfg.walk_cost)
        elif action == "Reproduce":
            sim.try_reproduce(self)
        elif action == "Rest":
            self.gain_energy(cfg.rest_gain)
        else:
            self.move_to(sim.random_neighbor(self), cfg.walk_cost * 0.7)
        self.lifecycle(cfg.metabolism)

    def can_reproduce(self, sim) -> bool:
        return (
            self.energy >= settings.WOLF.reproduce_energy
            and self.reproduction_cooldown <= 0
            and sim.count_species("Wolf") < settings.WOLF.max_population
        )
