"""Проверка опубликованных таблиц ПЭМ; только стандартная библиотека Python."""

from collections import Counter
import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIELDS = ("sample_id", "image_id", "particle_no", "size_nm", "source_cell", "import_note")
MANIFEST_FIELDS = ("sample_id", "status", "n_images", "n_labeled", "n_unlabeled", "note")


def read_csv(path, fields):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == fields, f"Unexpected columns in {path.name}"
        return list(reader)


def main():
    records = read_csv(ROOT / "measurements.csv", FIELDS)
    manifest = read_csv(ROOT / "source_manifest.csv", MANIFEST_FIELDS)
    assert len(records) == 6625
    assert len(manifest) == 22
    assert len({r["sample_id"] for r in manifest}) == 22

    included = {r["sample_id"] for r in manifest if r["status"] == "included"}
    excluded = {r["sample_id"] for r in manifest if r["status"] == "excluded"}
    assert len(included) == 20 and excluded == {"V14", "V16"}
    assert {r["sample_id"] for r in records} == included

    particles = set()
    source_cells = set()
    fields = set()
    sample_counts = Counter()
    comma_notes = 0
    for r in records:
        key = (r["sample_id"], r["image_id"], int(r["particle_no"]))
        assert key not in particles and key[2] > 0
        particles.add(key)
        fields.add(key[:2])
        sample_counts[key[0]] += 1
        assert r["source_cell"] not in source_cells
        source_cells.add(r["source_cell"])
        size = float(r["size_nm"])
        assert math.isfinite(size) and size > 0
        assert r["import_note"] in ("", "decimal_comma")
        comma_notes += r["import_note"] == "decimal_comma"

    assert len(fields) == 90 and comma_notes == 8
    n_fields = Counter(sample_id for sample_id, _ in fields)
    for r in manifest:
        if r["status"] == "included":
            assert sample_counts[r["sample_id"]] == int(r["n_labeled"])
            assert n_fields[r["sample_id"]] == int(r["n_images"])
            assert int(r["n_unlabeled"]) == 0
        else:
            assert r["sample_id"] not in sample_counts
    assert sum(int(r["n_unlabeled"]) for r in manifest) == 213
    print("OK: 20 образцов, 90 снимков, 6625 измерений; V14/V16 исключены")


if __name__ == "__main__":
    main()
