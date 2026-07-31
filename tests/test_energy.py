import settings
from simulation import Simulation
import unittest


class EnergyTests(unittest.TestCase):
    def test_animals_lose_energy_over_time(self):
        sim = Simulation(settings.SimulationConfig(seed=1))
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.energy = 80
        rabbit.current_action = "Wander"
        before = rabbit.energy
        rabbit.lifecycle(settings.RABBIT.metabolism)
        self.assertLess(rabbit.energy, before)

    def test_rabbits_gain_energy_when_eating(self):
        sim = Simulation(settings.SimulationConfig(seed=2))
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.energy = 20
        sim.world.grass[rabbit.y][rabbit.x] = 3
        rabbit.current_action = "Eat grass"
        rabbit.act(sim)
        self.assertGreater(rabbit.energy, 20)

    def test_wolves_gain_energy_after_successful_hunt(self):
        sim = Simulation(settings.SimulationConfig(seed=3))
        wolf = sim.animals_by_species("Wolf")[0]
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.x, rabbit.y = wolf.x + 1, wolf.y
        if sim.world.is_blocked(rabbit.x, rabbit.y):
            rabbit.x, rabbit.y = wolf.x, wolf.y
        wolf.energy = 50
        sim.rng.random = lambda: 0.0
        self.assertTrue(sim.try_hunt(wolf, rabbit))
        self.assertGreater(wolf.energy, 50)
        self.assertFalse(rabbit.alive)

    def test_animals_die_when_energy_reaches_zero(self):
        sim = Simulation(settings.SimulationConfig(seed=4))
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.energy = 0
        rabbit.lifecycle(settings.RABBIT.metabolism)
        self.assertFalse(rabbit.alive)
        self.assertEqual(rabbit.death_reason, "starvation")
