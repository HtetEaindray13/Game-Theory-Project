import settings
from simulation import Simulation
import unittest


class ReproductionTests(unittest.TestCase):
    def test_reproduction_respects_energy_and_cooldown(self):
        sim = Simulation(settings.SimulationConfig(seed=9))
        a, b = sim.animals_by_species("Rabbit")[:2]
        b.x, b.y = a.x, a.y
        a.energy = settings.RABBIT.reproduce_energy - 1
        a.reproduction_cooldown = 0
        before = sim.count_species("Rabbit")
        self.assertFalse(sim.try_reproduce(a))
        self.assertEqual(sim.count_species("Rabbit"), before)
        a.energy = settings.RABBIT.reproduce_energy + 5
        a.reproduction_cooldown = 10
        self.assertFalse(sim.try_reproduce(a))
        self.assertEqual(sim.count_species("Rabbit"), before)

    def test_successful_reproduction_adds_one_animal(self):
        sim = Simulation(settings.SimulationConfig(seed=10))
        a, b = sim.animals_by_species("Rabbit")[:2]
        b.x, b.y = a.x, a.y
        a.energy = settings.RABBIT.reproduce_energy + 10
        a.reproduction_cooldown = 0
        before = sim.count_species("Rabbit")
        self.assertTrue(sim.try_reproduce(a))
        self.assertEqual(sim.count_species("Rabbit"), before + 1)
        self.assertEqual(a.reproduction_cooldown, settings.RABBIT.reproduce_cooldown)
