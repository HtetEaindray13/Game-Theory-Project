import unittest

import settings
from simulation import Simulation


class WildlifeTests(unittest.TestCase):
    def test_every_species_spawns(self):
        sim = Simulation()
        for species in settings.SPECIES_PROFILES:
            self.assertGreater(sim.count_species(species), 0, species)

    def test_wolf_is_hurt_for_attacking_lion(self):
        sim = Simulation()
        wolf = sim.animals_by_species("Wolf")[0]
        lion = sim.animals_by_species("Lion")[0]
        lion.x, lion.y = wolf.x + 1, wolf.y
        wolf.health = 100
        sim.rng.random = lambda: 0.0
        sim.try_attack(wolf, lion)
        self.assertLess(wolf.health, 100)

    def test_snake_venom_poison_and_slow(self):
        sim = Simulation()
        snake = sim.animals_by_species("Snake")[0]
        rabbit = sim.animals_by_species("Rabbit")[0]
        rabbit.x, rabbit.y = snake.x + 1, snake.y
        sim.rng.random = lambda: 0.0
        sim.try_attack(snake, rabbit)
        self.assertGreater(rabbit.poison_ticks, 0)
        self.assertGreater(rabbit.slowed_ticks, 0)

    def test_elephant_counter_stuns_attacker(self):
        sim = Simulation()
        wolf = sim.animals_by_species("Wolf")[0]
        elephant = sim.animals_by_species("Elephant")[0]
        elephant.x, elephant.y = wolf.x + 1, wolf.y
        sim.rng.random = lambda: 0.0
        sim.try_attack(wolf, elephant)
        self.assertGreater(wolf.stunned_ticks, 0)

    def test_crocodiles_spawn_in_wet_habitat(self):
        sim = Simulation()
        habitats = settings.SPECIES_PROFILES["Crocodile"].habitat
        for crocodile in sim.animals_by_species("Crocodile"):
            self.assertIn(sim.world.terrain[crocodile.y][crocodile.x], habitats)


if __name__ == "__main__":
    unittest.main()
