"""Check the manifest and the exact JPEGs used in the microscopy exercise."""

from __future__ import annotations

import csv
import hashlib
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageCms


HERE = Path(__file__).resolve().parent
EXPECTED = {
    "1a.JPG",
    "1b.jpg",
    "2016-02-26-n1-1-4.jpg",
    "2019-02-18-2-6035.jpg",
    "2019-12-13-9-2.jpg",
}
FIELDS = {
    "image_id", "source_file", "case", "modality_evidence", "scale_bar_value",
    "scale_bar_unit", "width_px", "height_px", "icc_profile", "sha256_raw",
}


def main() -> None:
    with (HERE / "manifest.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames is not None and set(reader.fieldnames) == FIELDS
        rows = list(reader)

    names = [Path(row["source_file"]).name for row in rows]
    assert set(names) == EXPECTED and len(names) == len(EXPECTED)
    assert len({row["image_id"] for row in rows}) == len(EXPECTED)
    assert {p.name for p in (HERE / "raw").iterdir() if p.is_file()} == EXPECTED

    for row in rows:
        source = HERE / row["source_file"]
        assert source.resolve().parent == (HERE / "raw").resolve()
        contents = source.read_bytes()
        assert hashlib.sha256(contents).hexdigest() == row["sha256_raw"], source
        with Image.open(BytesIO(contents)) as im:
            assert im.format == "JPEG" and im.mode == "RGB", source
            assert (im.width, im.height) == (
                int(row["width_px"]), int(row["height_px"])
            ), source
            profile = ImageCms.ImageCmsProfile(BytesIO(im.info["icc_profile"]))
            assert ImageCms.getProfileName(profile).strip() == row["icc_profile"], source
        assert (row["scale_bar_value"] == "") == (row["scale_bar_unit"] == ""), source
        print(f"OK {row['image_id']} {row['source_file']}")

    print("5 original images verified")


if __name__ == "__main__":
    main()
