import settings
from simulation import Simulation
import unittest


class DecisionTests(unittest.TestCase):
    def test_rabbit_prefers_hide_or_escape_when_wolf_close(self):
        sim = Simulation(settings.SimulationConfig(seed=5))
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.strategy = "Cautious"
        rabbit.energy = 80
        wolf = sim.animals_by_species("Wolf")[0]
        wolf.x, wolf.y = rabbit.x + 1, rabbit.y
        if sim.world.is_blocked(wolf.x, wolf.y):
            wolf.x, wolf.y = rabbit.x, rabbit.y
        rabbit.decide(sim)
        self.assertIn(rabbit.current_action, {"Hide", "Escape"})

    def test_hungry_rabbit_prefers_food_without_predator(self):
        sim = Simulation(settings.SimulationConfig(seed=6))
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.strategy = "Bold"
        rabbit.energy = 12
        for wolf in sim.animals_by_species("Wolf"):
            wolf.x, wolf.y = 0, 0
        sim.world.grass[rabbit.y][rabbit.x] = 3
        rabbit.decide(sim)
        self.assertEqual(rabbit.current_action, "Eat grass")

    def test_starving_wolf_prefers_hunting_when_prey_reachable(self):
        sim = Simulation(settings.SimulationConfig(seed=7))
        wolf = sim.animals_by_species("Wolf")[0]
        wolf.strategy = "Aggressive"
        wolf.energy = 20
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.x, rabbit.y = wolf.x + 1, wolf.y
        if sim.world.is_blocked(rabbit.x, rabbit.y):
            rabbit.x, rabbit.y = wolf.x, wolf.y
        wolf.decide(sim)
        self.assertIn(wolf.current_action, {"Hunt rabbit", "Chase rabbit"})

    def test_animals_cannot_move_into_blocked_tiles(self):
        sim = Simulation(settings.SimulationConfig(seed=8))
        rabbit = sim.animals_by_species("Rabbit")[0]
        x, y = rabbit.x, rabbit.y
        blocked = None
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if sim.world.in_bounds(nx, ny):
                sim.world.terrain[ny][nx] = settings.TERRAIN_WATER
                blocked = (nx, ny)
                break
        self.assertIsNotNone(blocked)
        self.assertNotIn(blocked, list(sim.world.neighbors(x, y)))
