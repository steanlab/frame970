# Colours of the 970Q-N panel (measured)

Repo path: `steanlab/frame970` → `docs/COLOUR.md`

Measured in November 2026 from four RAW (DNG) photos of the calibration charts "Colours and mixing" and "Gradients"
(Pixel phone, black level 256 subtracted, linear data, 23 °C, a sheet of white paper next to the panel).
The lighting in the photos was uneven (up to ±25 % across the panel), so every field was divided by the panel's own white
next to it. The numbers are estimates, good to roughly ±15 %.

| colour | linear light relative to the panel white | sRGB for the preview |
|---|---|---|
| white | 1.00, 1.00, 1.00 | 255, 255, 255 |
| black | about 0.06 (dark grey, not 0) | about 70, 70, 70 |
| red | 0.70, 0.31, 0.05 | 218, 151, 63 (orange-ish) |
| yellow | 1.00, 0.70, 0.08 | 255, 218, 80 (golden) |

* The panel white itself is about 0.65 of white paper and slightly yellowish.
* Mixing dots of two colours (Bayer steps in the "Colours and mixing" ramps) is close to linear in light, so the right place to dither is **linear light**.
* The old page dithered sRGB values with a perfect black and white. Mid-greys then came out much too light:
  a 50 % grey (sRGB 128, should reflect 22 %) turned into 50 % white dots, i.e. about 53 % reflectance.
  The flat grey fields of the "Gradients" chart measured 0.23 / 0.45 / 0.85 (relative to white) for the 25 / 50 / 75 % fields, matching that prediction.
* Black readings differ between photos (0.07 … 0.28 of white) because of reflections in the glass. 0.06 is the dark end of the range.

The page has a switch "palette: measured / nominal". "measured" works in linear light with these colours;
"nominal" is the old behaviour. The values are in `PAL_LIN` in `docs/index.html`; edit them if you measure better.
