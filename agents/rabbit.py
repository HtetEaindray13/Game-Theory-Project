import settings
from agents.animal import Animal
from ai import strategies, utility_ai


class Rabbit(Animal):
    def __init__(self, x, y, rng, strategy: str | None = None):
        cfg = settings.RABBIT
        super().__init__("Rabbit", x, y, strategy or strategies.random_rabbit_strategy(rng), rng)
        self.energy = rng.uniform(58, cfg.max_energy)
        self.max_energy = cfg.max_energy
        self.max_age = cfg.max_age
        self.speed = cfg.speed
        self.vision_range = cfg.vision_range
        self.reproduction_cooldown = rng.randint(15, cfg.reproduce_cooldown)

    def decide(self, sim) -> None:
        obs = sim.observe(self)
        scores, reason = utility_ai.rabbit_scores(self, obs, sim.world, sim)
        self.last_action_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
        self.current_action = max(scores, key=scores.get)
        self.last_decision_reason = reason
        self.target = obs.get("nearest_wolf") or obs.get("nearest_grass") or obs.get("nearest_shelter")

    def act(self, sim) -> None:
        cfg = settings.RABBIT
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
        if action == "Eat grass" and sim.world.grass_amount(self.x, self.y) > 0:
            eaten = sim.world.eat_grass(self.x, self.y, settings.GRASS_EAT_AMOUNT)
            self.food_eaten += eaten
            self.gain_energy(eaten * settings.RABBIT_EAT_GAIN)
        elif action == "Move toward grass":
            self.move_to(sim.world.step_toward(self.pos, obs["nearest_grass"]), cfg.walk_cost)
        elif action == "Hide":
            if not sim.world.is_shelter(self.x, self.y):
                self.move_to(sim.world.step_toward(self.pos, obs["nearest_shelter"]), cfg.walk_cost)
            else:
                self.energy -= cfg.metabolism * 0.25
        elif action == "Escape":
            self.move_to(sim.world.step_away(self.pos, obs["nearest_wolf"]), cfg.chase_cost)
            self.successful_escapes += 1 if obs["nearest_wolf"] else 0
        elif action == "Reproduce":
            sim.try_reproduce(self)
        elif action == "Rest":
            self.gain_energy(cfg.rest_gain)
        else:
            self.move_to(sim.random_neighbor(self), cfg.walk_cost * 0.6)
        self.lifecycle(cfg.metabolism)

    def can_reproduce(self, sim) -> bool:
        return (
            self.energy >= settings.RABBIT.reproduce_energy
            and self.reproduction_cooldown <= 0
            and sim.count_species("Rabbit") < settings.RABBIT.max_population
        )
