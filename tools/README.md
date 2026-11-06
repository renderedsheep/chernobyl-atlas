# Map-building tools

Python scripts that turn the eight General Staff 1:100 000 scans into the map tiles used by the atlas. You only need these to rebuild the base map, for example from sharper scans.

Requirements: Python 3 with `numpy`, `opencv-python`, `Pillow`.

| Step | Script | What it does |
|---|---|---|
| 1 | `corners.py` | Finds the inner frame (neatline) corners of each scan in `src/`. Writes `work/corners.json`. |
| 2 | `warp.py` | Shifts each sheet from СК-42 (Pulkovo 1942) to WGS 84, reprojects to Web Mercator at zoom 13 and joins the sheets. Writes `work/mosaic.npy`. |
| 3 | `colormatch.py` | Matches the colour of the two brighter scans to the rest. |
| 4 | `tiles.py` | Cuts the mosaic into 1024 px WebP tiles in `tiles/`. Copy that folder over `../tiles`. |
| 5 | `water.py` | Traces the blue water fill into polygons and writes `../data/water.js`. |
| (aid) | `cells.py` | Cuts the mosaic into gridded crops used to read settlement names and populations by eye. |

Run them from this folder, in order. `geo.py` holds the datum shift and projection maths shared by the others.

`src/` holds the scans, named by sheet (`M-36-13.jpg` …). Sheet corners in `corners.py` assume the standard 20′ × 30′ layout of 1:100 000 sheets; a new scan with a different margin may need its corners checked by eye (the script writes `work/corners_check.png` for that).

`readings/settlement_readings.txt` is the log of positions read from the crops: `cell|kind|name|x|y|population|note`.
