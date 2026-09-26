"""Synthetic starter tables for production/13-homework.md.

Run from the repository root with
    python -m production.examples.lecture13_homework_inputs

The deterministic sensor values and DLS repeats are invented for practising
table relations and time windows. They are not instrument exports, extra
independent batches, or a physical process model.
"""

import pandas as pd


def make_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return batches, samples, measurements and minute-level sensor rows."""
    design = [
        ("B01", 2, "R1", "L1", 115), ("B02", 2, "R1", "L2", 118),
        ("B03", 2, "R2", "L1", 110), ("B04", 2, "R2", "L2", 112),
        ("B05", 20, "R1", "L1", 126), ("B06", 20, "R1", "L2", 128),
        ("B07", 20, "R2", "L1", 118), ("B08", 20, "R2", "L2", 120),
    ]
    batches = pd.DataFrame(design, columns=[
        "batch_id", "scale_l", "recipe_version", "raw_lot", "nominal_mean_nm"
    ])
    samples = pd.DataFrame([
        (f"{bid}-{position}", bid, position, 35)
        for bid, *_ in design for position in ("top", "bottom")
    ], columns=["sample_id", "batch_id", "position", "draw_minute"])

    # These offsets make the four invented readings average to the published
    # nominal batch value. They add no new experimental information.
    measurements = samples[["sample_id", "batch_id", "position"]].merge(
        batches[["batch_id", "nominal_mean_nm"]],
        on="batch_id", validate="many_to_one"
    )
    measurements = measurements.loc[measurements.index.repeat(2)].copy()
    measurements["repeat_index"] = measurements.groupby("sample_id").cumcount() + 1
    measurements["measurement_id"] = (
        measurements.sample_id + "-M" + measurements.repeat_index.astype(str)
    )
    measurements["size_nm"] = (
        measurements.nominal_mean_nm
        + measurements.position.map({"top": -1.0, "bottom": 1.0})
        + measurements.repeat_index.map({1: -0.25, 2: 0.25})
    )
    measurements["available_minute"] = 50
    measurements = measurements.drop(columns="nominal_mean_nm")

    # Minute 0..50, in minutes relative to each separate batch start.
    # Values after the draw at minute 35 must not enter a draw-time prediction.
    sensor = pd.DataFrame([
        (bid, minute,
         25 + 0.09 * max(minute - 10, 0) + (0.4 if scale == 20 else 0),
         8.2 - 0.008 * max(minute - 10, 0) - (0.04 if recipe == "R2" else 0))
        for bid, scale, recipe, _, _ in design for minute in range(51)
    ], columns=["batch_id", "minute", "temp_c", "ph"])
    assert (len(batches), len(samples), len(measurements), len(sensor)) == (8, 16, 32, 408)
    assert batches.batch_id.is_unique and samples.sample_id.is_unique
    assert measurements.measurement_id.is_unique
    assert not sensor.duplicated(["batch_id", "minute"]).any()
    return batches, samples, measurements, sensor


if __name__ == "__main__":
    batches, samples, measurements, sensor = make_inputs()
    print("Стартовые таблицы (строк):", {
        "batches": len(batches), "samples": len(samples),
        "measurements": len(measurements), "sensor": len(sensor),
    })
