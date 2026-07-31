import unittest

from simulation import Simulation


class PlayerModeTests(unittest.TestCase):
    def test_can_choose_each_species(self):
        for species in ("Rabbit", "Wolf", "Lion"):
            sim = Simulation()
            player = sim.start_player(species)
            self.assertIsNotNone(player)
            self.assertEqual(player.species, species)
            self.assertEqual(sim.selected_id, player.id)

    def test_player_movement_respects_blocked_tiles(self):
        sim = Simulation()
        player = sim.start_player("Rabbit")
        start = player.pos
        sim.world.terrain[player.y][player.x + 1] = "water"
        sim.step("right")
        self.assertEqual(player.pos, start)

    def test_rabbit_player_can_graze(self):
        sim = Simulation()
        player = sim.start_player("Rabbit")
        sim.world.grass[player.y][player.x] = 3
        player.energy = 40
        sim.step("interact")
        self.assertGreater(sim.player_food, 0)
        self.assertGreater(player.energy, 40)

    def test_player_score_increases_with_survival(self):
        sim = Simulation()
        sim.start_player("Wolf")
        before = sim.player_score()
        sim.step("rest")
        self.assertGreater(sim.player_score(), before)

    def test_lion_uses_hunt_objective(self):
        sim = Simulation()
        sim.start_player("Lion")
        objective, progress = sim.player_objective()
        self.assertEqual(objective, "Successful hunts")
        self.assertEqual(progress, 0)

    def test_resting_slowly_restores_player_health(self):
        sim = Simulation()
        player = sim.start_player("Wolf")
        player.health = 60
        sim.step("rest")
        self.assertGreater(player.health, 60)
        self.assertLessEqual(player.health, 100)

    def test_rest_does_not_heal_through_venom(self):
        sim = Simulation()
        player = sim.start_player("Lion")
        player.health = 60
        player.poison_ticks = 4
        player.poison_damage = 1
        sim.step("rest")
        self.assertLess(player.health, 60)


if __name__ == "__main__":
    unittest.main()
