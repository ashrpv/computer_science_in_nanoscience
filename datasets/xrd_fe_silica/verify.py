"""Проверка происхождения и структуры восьми опубликованных XRD-файлов."""

import csv
import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_xy(path):
    x, intensity = [], []
    for line_no, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        values = line.split()
        if len(values) != 2:
            raise ValueError(f"{path.name}:{line_no}: ожидались два числовых поля")
        angle, signal = map(float, values)
        if not all(map(math.isfinite, (angle, signal))):
            raise ValueError(f"{path.name}:{line_no}: нечисловой/неконечный отсчёт")
        x.append(angle)
        intensity.append(signal)
    if len(x) != 1888 or not all(b > a for a, b in zip(x, x[1:])):
        raise ValueError(f"{path.name}: число точек или монотонность оси")
    if min(intensity) < 0:
        raise ValueError(f"{path.name}: отрицательное исходное показание")
    return x, intensity


def main():
    with (ROOT / "manifest.csv").open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 8 or len({row["sample_id"] for row in rows}) != 8:
        raise ValueError("Ожидались восемь уникальных физических образцов")
    if sum(row["material"] == "silica_only" for row in rows) != 2:
        raise ValueError("Ожидались два контроля SiO₂")

    reference_grid = None
    for row in rows:
        path = ROOT / row["source_file"]
        if path.parent != ROOT / "raw" or not path.is_file():
            raise ValueError(f"Нет исходного файла для {row['sample_id']}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row["sha256_raw"]:
            raise ValueError(f"{path.name}: контрольная сумма не совпадает")
        x, _ = read_xy(path)
        if reference_grid is None:
            reference_grid = x
        elif x != reference_grid:
            raise ValueError(f"{path.name}: угловая сетка отличается")

    steps = [b - a for a, b in zip(reference_grid, reference_grid[1:])]
    if not (reference_grid[0] == 5 and max(steps) - min(steps) < 2e-5):
        raise ValueError("Начало оси или разброс шага неожиданны")
    print(
        f"OK: {len(rows)} независимых образцов; {len(rows) * len(reference_grid)} "
        f"точек; сетка {reference_grid[0]:.5f}–{reference_grid[-1]:.5f}°, "
        f"шаг {sum(steps) / len(steps):.5f}°; SHA-256 всех файлов совпали."
    )


if __name__ == "__main__":
    main()
