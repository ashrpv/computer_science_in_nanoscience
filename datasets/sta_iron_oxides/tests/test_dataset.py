"""Scientific integrity checks for the published STA exercise."""
import csv
import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prepare import FIELDS, parse, sha256


class DatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "manifest.csv").open(encoding="utf-8", newline="") as file:
            cls.manifest = list(csv.DictReader(file))

    def test_complete_series_and_checksums(self):
        self.assertEqual({r["run_id"] for r in self.manifest},
                         {"028", "043", "105", "106", "107", "108", "197", "198", "200", "201", "202"})
        self.assertEqual(sum(int(r["n_points"]) for r in self.manifest), 82325)
        for row in self.manifest:
            with self.subTest(run=row["run_id"]):
                for kind in ("raw", "processed"):
                    path = ROOT / kind / f'sta_{row["run_id"]}.csv'
                    self.assertEqual(sha256(path), row[f"{kind}_sha256"])

    def test_numeric_values_and_missing_channels(self):
        for row in self.manifest:
            run = row["run_id"]
            with self.subTest(run=run):
                _, columns, original = parse(ROOT / "raw" / f"sta_{run}.csv")
                with (ROOT / "processed" / f"sta_{run}.csv").open(encoding="utf-8", newline="") as file:
                    reader = csv.DictReader(file)
                    self.assertEqual(reader.fieldnames, FIELDS)
                    processed = list(reader)
                self.assertEqual(original, processed)
                self.assertEqual(len(original), int(row["n_points"]))
                self.assertEqual([int(r["point_index"]) for r in original], list(range(len(original))))
                self.assertTrue(all(float(b["time_min"]) >= float(a["time_min"])
                                    for a, b in zip(original, original[1:])))
                has_mass = "Mass/%" in columns
                self.assertEqual(has_mass, row["has_mass"] == "True")
                if not has_mass:
                    self.assertTrue(all(r["mass_pct"] == "" for r in original))

    def test_anonymization_and_program_boundaries(self):
        for row in self.manifest:
            raw = (ROOT / "raw" / f'sta_{row["run_id"]}.csv').read_text(encoding="utf-8")
            self.assertIn("#OPERATOR:;operator_redacted", raw)
            self.assertNotIn("Шарапаев", raw)
        _, _, records = parse(ROOT / "raw" / "sta_197.csv")
        self.assertEqual(set(r["segment"] for r in records), {"1", "2"})
        self.assertIn("134", next(r["identity_header"] for r in self.manifest if r["run_id"] == "198"))
        self.assertIn("subtr.3", next(r["dsc_channel"] for r in self.manifest if r["run_id"] == "043"))


if __name__ == "__main__":
    unittest.main()
