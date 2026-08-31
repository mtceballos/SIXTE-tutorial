"""Build the Phase 3 east/west flat semicircle morphology images."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runtime" / "phase3-mixing"


def main() -> None:
    size = 101
    center = (size - 1) / 2
    y, x = np.indices((size, size), dtype=float)
    circle = (x - center) ** 2 + (y - center) ** 2 < 50.0**2
    east = circle & (x > center)
    west = circle & (x < center)

    wcs = WCS(naxis=2)
    wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    wcs.wcs.crval = [45.0, 0.0]
    wcs.wcs.crpix = [center + 1, center + 1]
    wcs.wcs.cdelt = [3.0 / 60.0 / size, 3.0 / 60.0 / size]
    header = wcs.to_header()

    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, mask in (("east", east), ("west", west)):
        image = np.where(mask, 100.0, 0.0).astype(np.float32)
        fits.writeto(
            OUTPUT / f"mixing_simput_img_{name}.fits",
            image,
            header,
            overwrite=True,
        )

    combined = np.where(circle, 100.0, 0.0).astype(np.float32)
    fits.writeto(OUTPUT / "mixing_simput_img.fits", combined, header, overwrite=True)


if __name__ == "__main__":
    main()
