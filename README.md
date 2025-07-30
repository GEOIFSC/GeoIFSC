# GeoIFSC

This repository contains small utilities for geographic data processing.

## Raster tiler

`raster_tiler.py` splits a large raster into a grid of tiles so that each
tile is approximately below a given size (default 50MB). It relies on
GDAL's Python bindings.

### Usage

```bash
python raster_tiler.py input.tif output_directory --max-size 50
```

Ensure the output directory already exists. Tiles will be named
`tile_row_col.tif` and compressed with LZW by default.
