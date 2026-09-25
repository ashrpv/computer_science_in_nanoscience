"""Check transcription integrity and the teaching cases' key limitations.

Run from any directory: python projects/regression_cases/verify.py
No modelling assumptions or undocumented repairs are applied here.
"""

import csv
from collections import Counter
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "data"
EXPECTED = [21, 67, 40, 14, 23, 36, 15, 9, 16]


def read(number):
    with (ROOT / f"variant_{number:02d}.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == EXPECTED[number - 1], (number, len(rows))
    assert [int(row["source_row"]) for row in rows] == list(range(1, len(rows) + 1)), number
    return rows


def verify():
    assert sorted(p.name for p in ROOT.glob("*.csv")) == [f"variant_{n:02d}.csv" for n in range(1, 10)]
    cases = {n: read(n) for n in range(1, 10)}

    one = cases[1]
    assert sum(bool(r["diameter_nm"]) and bool(r["size_sd_nm"]) for r in one) == 20
    assert one[8]["fe3_fe2_ratio"] == "0,"
    assert one[18]["diameter_nm"] == one[18]["size_sd_nm"] == ""

    two = cases[2]
    assert any("магнитная мешалка" in r["salt_mass_raw"] for r in two)
    assert any("1200" in r["synthesis_temperature_raw"] for r in two)

    three = cases[3]
    factor_pairs = Counter((r["speed_mm_s"], r["energy_nJ"]) for r in three)
    assert len(factor_pairs) == 10 and set(factor_pairs.values()) == {4}
    assert {energy for speed, energy in factor_pairs if speed == "2"} == {"0.1", "0.2"}
    assert {r["etch_min"] for r in three} == {"30"}

    four = cases[4]
    assert "time" not in " ".join(four[0].keys()).lower()
    five = cases[5]
    assert [r["source_row"] for r in five if not r["diameter_nm"] and not r["size_sd_nm"]] == ["21"]

    six = cases[6]
    kerosene = {(r["cosurfactant_level"], r["w_water_to_surfactant"]) for r in six if r["kerosene_droplet_nm"]}
    other = {(r["cosurfactant_level"], r["w_water_to_surfactant"]) for r in six if r["nonkerosene_droplet_nm"]}
    assert (len(kerosene), len(other), len(kerosene & other)) == (31, 16, 11)

    seven = cases[7]
    configs = Counter((r["zinc_acetate_to_oxalic_ratio"], r["ph"], r["calcination_C"]) for r in seven)
    assert len(configs) == 14 and configs[("3", "5", "600")] == 2
    assert {r["crystallite_nm"] for r in seven if (r["zinc_acetate_to_oxalic_ratio"], r["ph"], r["calcination_C"]) == ("3", "5", "600")} == {"43", "52"}

    eight = cases[8]
    assert eight[8]["homogenization_rpm"] == eight[8]["homogenization_rpm_raw"] == "1000"
    assert eight[4]["pdi"] == "1.011"
    assert Counter(r["homogenization_rpm"] for r in eight) == Counter({"10000": 2, "15000": 3, "20000": 3, "1000": 1})

    nine = cases[9]
    assert sorted(int(r["measurement_order"]) for r in nine) == list(range(1, 17))
    factors = ("aging_h", "ultrasound_min", "hybrid_mass_pct", "hydrocarbon", "surfactant")
    for left, right in combinations(factors, 2):
        assert len({(r[left], r[right]) for r in nine}) == 16, (left, right)
    assert nine[6]["droplet_um"] == "0.80"
    assert abs(sum((0.89, 0.76, 0.83, 0.86)) / 4 - 0.835) < 1e-12
    assert nine[6]["response_raw"] == "(0.89, 0.76, 0.83, 0.86) 0.80 = y7"
    print("OK: nine cases, row counts, factor coverage and unresolved source discrepancies")


if __name__ == "__main__":
    verify()
