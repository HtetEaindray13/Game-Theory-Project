import csv
import tempfile
import unittest

import settings
from simulation import CSV_COLUMNS, Simulation


class PopulationTests(unittest.TestCase):
    def test_population_counters_remain_accurate(self):
        sim = Simulation(settings.SimulationConfig(seed=11))
        rabbits = sim.count_species("Rabbit")
        wolves = sim.count_species("Wolf")
        self.assertEqual(rabbits, settings.PRESETS["balanced"].rabbits)
        self.assertEqual(wolves, settings.PRESETS["balanced"].wolves)

    def test_reset_restores_configured_initial_state(self):
        sim = Simulation(settings.SimulationConfig(seed=12))
        sim.step()
        sim.reset("decline")
        self.assertEqual(sim.tick, 0)
        self.assertEqual(sim.count_species("Rabbit"), settings.PRESETS["decline"].rabbits)
        self.assertEqual(sim.count_species("Wolf"), settings.PRESETS["decline"].wolves)

    def test_csv_records_expected_columns(self):
        config = settings.SimulationConfig(seed=13)
        with tempfile.TemporaryDirectory() as tmpdir:
            config.data_path = f"{tmpdir}/simulation_results.csv"
            sim = Simulation(config)
            sim.step()
            sim.record_history()
            sim.save_csv()
            with open(config.data_path, newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, CSV_COLUMNS)
                rows = list(reader)
        self.assertTrue(rows)
