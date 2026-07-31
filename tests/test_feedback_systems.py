import unittest

from ai import payoff
from simulation import Simulation


class FeedbackSystemTests(unittest.TestCase):
    def test_payoff_breakdown_matches_total(self):
        sim = Simulation()
        animal = sim.animals[0]
        animal.age = 30
        animal.energy_gained = 12
        animal.wasted_energy = 4
        breakdown = payoff.payoff_breakdown(animal)
        self.assertAlmostEqual(sum(breakdown.values()), payoff.calculate_animal_payoff(animal))

    def test_attack_creates_animation_and_sound_event(self):
        sim = Simulation()
        wolf = sim.animals_by_species("Wolf")[0]
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.x, rabbit.y = wolf.x + 1, wolf.y
        sim.rng.random = lambda: 0.0
        sim.try_attack(wolf, rabbit)
        self.assertEqual(wolf.animation, "attack")
        self.assertTrue(any(event["kind"] == "attack" for event in sim.events))

    def test_dead_animals_leave_temporary_animation(self):
        sim = Simulation()
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.die("test")
        sim.collect_dead()
        self.assertTrue(sim.death_animations)
        self.assertEqual(sim.death_animations[-1]["species"], "Rabbit")
        self.assertTrue(any(event["kind"] == "death" for event in sim.events))


if __name__ == "__main__":
    unittest.main()
