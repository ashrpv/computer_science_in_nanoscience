"""Regenerate rectangular CSVs from the published anonymized NETZSCH exports.

Run from any directory: python datasets/sta_iron_oxides/prepare.py
The raw files are UTF-8, with their original numeric lines and delimiters.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ["run_id", "point_index", "temperature_C", "time_min", "dsc_mW_mg",
          "mass_pct", "purge1_ml_min", "purge2_ml_min", "protective_ml_min",
          "sensitivity_uV_mW", "segment"]
NAMES = {"##Temp./°C": "temperature_C", "Time/min": "time_min",
         "Mass/%": "mass_pct", "Gas Flow(purge1)/(ml/min)": "purge1_ml_min",
         "Gas Flow(purge2)/(ml/min)": "purge2_ml_min",
         "Gas Flow(protective)/(ml/min)": "protective_ml_min",
         "Sensit./(uV/mW)": "sensitivity_uV_mW", "Segment": "segment"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    header_at = next(i for i, line in enumerate(lines) if line.startswith("##Temp./°C;"))
    meta = {}
    for line in lines[:header_at]:
        if line.startswith("#") and ":" in line:
            key, value = line[1:].split(":", 1)
            meta[key.strip()] = value.lstrip("; ").strip()
    columns = lines[header_at].split(";")
    if not any(c.startswith("DSC") and c.endswith("/(mW/mg)") for c in columns):
        raise ValueError(f"Unknown DSC column in {path}")
    names = [("dsc_mW_mg" if c.startswith("DSC") and c.endswith("/(mW/mg)")
              else NAMES[c]) for c in columns]
    if len(names) != len(set(names)):
        raise ValueError(f"Duplicate columns in {path}")
    decimal = "," if meta["DECIMAL"] == "COMMA" else "."
    run_id = path.stem.removeprefix("sta_")
    segment_value = meta["SEGMENT"].split("/")[0]
    if segment_value.startswith("S") and "-" not in segment_value:
        segment_value = segment_value[1:]
    else:
        segment_value = ""  # Multi-segment runs must provide a Segment column.
    records = []
    for line in lines[header_at + 1:]:
        if not line.strip():
            continue
        values = [v.strip() for v in line.split(";")]
        if len(values) != len(columns):
            raise ValueError(f"Invalid data row in {path}: {line[:80]}")
        record = dict.fromkeys(FIELDS, "")
        record.update(zip(names, (v.replace(decimal, ".") if decimal == "," else v for v in values)))
        record["run_id"] = run_id
        record["point_index"] = str(len(records))
        if not record["segment"]:
            record["segment"] = segment_value
        if not record["segment"]:
            raise ValueError(f"Missing segment in {path}")
        records.append(record)
    return meta, columns, records


def main():
    out = ROOT / "processed"
    out.mkdir(exist_ok=True)
    for path in sorted((ROOT / "raw").glob("sta_*.csv")):
        _, _, records = parse(path)
        dest = out / path.name
        with dest.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)
        print(path.stem, len(records), sha256(dest))


if __name__ == "__main__":
    main()
