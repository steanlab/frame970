# Flashing the firmware (release candidate 0.9.0-rc1)

Repo path: `steanlab/frame970` → `firmware/FLASHING.md`

`frame970-0.9.0-rc1.bin` (SHA-256 in `SHA256SUMS.txt`) replaces the original firmware of the Nebular Pro 970Q-N. The tag has no update over Bluetooth, so **you need a wire to the chip, and your own backup of the stock flash to go back**.
The firmware source is not published. Use at your own risk, no warranty.

## What you need

- A tag **Nebular Pro 970Q-N** (the label on the housing says so). Other Hanshow tags have other pins and panels: this image will not work on them and may damage the data on them.
- A programmer that can read and write the tag's flash through the Telink debug wire (SWS) or directly on the external SPI flash chip. This guide does not cover a particular tool or the soldering points yet; check the pins and the flash map in [`docs/HARDWARE.md`](../docs/HARDWARE.md) and use the tool you trust.
- A battery in the tag (3 V lithium) or a 3 V supply.

## Before you flash

1. **Back up the stock flash first**: the full 1 MiB, read **twice** and compared byte for byte. It holds data that exists only on your tag:
   the panel waveforms (block `0xF8000`, 12 KiB), the factory record (`0xFE000`), the Bluetooth address and SDK settings (`0xFF000`).
   Do not publish the dump and do not flash it into another tag.
2. **Do not mass-erase** the chip. Write only the range of the firmware (`0x00000`.. file length) and leave the rest as it is.
   The firmware never writes `0xF8000`, `0xFE000` and `0xFF000`, but a wrong programmer setting can erase them.
3. Check the file: SHA-256 as in `SHA256SUMS.txt`; bytes 8..11 are `KNLT`; the 32-bit little-endian value at offset 0x18 is the file length (81 960). The file is already in Telink image form.
4. The firmware occupies `0x00000`..`0x2FFFF` at most. Picture slots start at `0x30000`; the area `0xF6000`..`0xF7FFF` holds the name and settings; see the flash map in `docs/HARDWARE.md`.

## Flash

1. Write `frame970-0.9.0-rc1.bin` at address `0x00000` of the flash.
2. Read it back and compare. Remove the programmer, insert the battery (or power-cycle).
3. The LED shows red, green, blue, red, green, blue (about 1 s): the firmware started.

## First check

1. Open <https://steanlab.github.io/frame970/> in Chrome or Edge, press **Connect**, pick `OD-xxxx` (tick "show all devices" if the list is empty).
2. The footer shows `page 0.9.0-rc1, protocol level 1 · tag firmware 0.9.0 (1)`. A warning banner appears when the levels differ.
3. In the card "Status" press the measure buttons: voltage near 3.0 V (fresh cell: 2.9..3.2 V), panel temperature near room temperature.
4. Upload a picture to a slot and press "show": the panel flickers for about 20 to 40 s and shows it; the LED flashes green twice.
5. A tag without connection goes to deep sleep after a few seconds when the slideshow is on: connect within the window after power-up, or at a wake-up (every 10..250 s, setting "poll").

## Going back to the stock firmware

Write your own backup of the stock flash back with the programmer (the whole 1 MiB, or at least everything except the picture slots and the settings areas).
Without a backup the original firmware cannot be restored: the factory data stays in the flash, but the stock firmware itself is not published anywhere.

## If something is wrong

- No LED sequence after power-up: check the supply, check the image (size, `KNLT` header), reflash.
- The tag does not appear in the device list: tick "show all devices" on the page; check that nothing else is connected to it.
- Panel stays blank or a refresh fails with three red flashes: read the log on the page (card "For developers"), try "reboot", check that block `0xF8000` is intact (the extractor `docs/tools/extract_waveforms.py` finds it on a dump).
- Report a problem in the Issues with the log from the page; please do not post MAC addresses, flash IDs or dumps.
