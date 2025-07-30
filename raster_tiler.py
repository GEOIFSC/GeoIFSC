#!/usr/bin/env python3
"""Split a raster into smaller tiles with approximate size limit.

This script uses GDAL to cut an input raster into a grid of tiles so that
no tile exceeds roughly ``max_size_mb``. The script estimates tile size
based purely on pixel count and data type; compression or metadata can
cause small deviations from the target size.

Example:
    python raster_tiler.py input.tif output_folder --max-size 50
"""

import os
import math
import argparse
from osgeo import gdal

def tile_raster(input_path: str, output_dir: str, max_size_mb: float = 50.0,
                compress: str = "LZW") -> None:
    """Cut ``input_path`` into tiles saved inside ``output_dir``.

    Parameters
    ----------
    input_path : str
        Path to the input raster.
    output_dir : str
        Directory where tiles will be written. It must exist.
    max_size_mb : float, optional
        Maximum size in megabytes for each tile. Default is 50MB.
    compress : str, optional
        Compression method passed to GDAL (e.g. "LZW", "DEFLATE").
    """
    ds = gdal.Open(input_path)
    if ds is None:
        raise RuntimeError(f"Unable to open {input_path}")

    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    bands = ds.RasterCount
    dtype_size = gdal.GetDataTypeSize(ds.GetRasterBand(1).DataType) // 8
    bytes_per_pixel = bands * dtype_size

    max_bytes = int(max_size_mb * 1024 * 1024)
    pixels_per_tile = max_bytes // bytes_per_pixel
    if pixels_per_tile <= 0:
        raise ValueError("max_size_mb too small for this raster's format")

    tile_size = int(math.sqrt(pixels_per_tile))
    if tile_size == 0:
        raise ValueError("Computed tile size is zero")

    cols = math.ceil(xsize / tile_size)
    rows = math.ceil(ysize / tile_size)

    for row in range(rows):
        for col in range(cols):
            x_off = col * tile_size
            y_off = row * tile_size
            width = tile_size if x_off + tile_size <= xsize else xsize - x_off
            height = tile_size if y_off + tile_size <= ysize else ysize - y_off

            out_name = f"tile_{row:03d}_{col:03d}.tif"
            out_path = os.path.join(output_dir, out_name)
            gdal.Translate(
                out_path,
                ds,
                srcWin=[x_off, y_off, width, height],
                creationOptions=[f"COMPRESS={compress}"]
            )
            print(f"Generated {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Split a raster into tiles")
    parser.add_argument("input_raster", help="Path to the input raster")
    parser.add_argument("output_dir", help="Existing directory for tiles")
    parser.add_argument("--max-size", type=float, default=50.0,
                        help="Max tile size in MB (default: 50)")
    parser.add_argument("--compress", default="LZW",
                        help="Compression method (default: LZW)")
    args = parser.parse_args()

    tile_raster(args.input_raster, args.output_dir,
                max_size_mb=args.max_size, compress=args.compress)


if __name__ == "__main__":
    main()

