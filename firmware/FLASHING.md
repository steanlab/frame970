# Test firmware

`frame970-test-4b.bin` (checksum in `SHA256SUMS.txt`) is a **test build**, not a release. It starts Bluetooth, deep sleep with timer wake-up, and LED / NFC probing commands for the control page.
It does not draw anything on the panel. The source is not published.

It replaces the original firmware of the Nebular Pro 970Q-N. The tag has no update over Bluetooth, so going back needs a wire and your own backup of the stock flash.

## Before flashing

1. **Back up the stock flash first** (a full 1 MiB dump, taken twice and compared). It holds the data of your tag: the panel waveforms at `0xF8000` and the factory record at `0xFE000`. Do not publish it and do not flash it into another tag.
   The firmware leaves `0xF8000` and `0xFE000` alone, but a wrong write can still destroy them.
2. Do not mass-erase the chip.
3. The image is a Telink image: bytes 8..11 are `KNLT` and the 32-bit value at offset 24 is the file length. The file here is already in that form.

How the tag is wired for programming and read-out is described in [`docs/HARDWARE.md`](../docs/HARDWARE.md); a step-by-step flashing guide will be added when the firmware gets a release.

## First check

Open the control page, press **Connect** and pick `n970-...`. The log shows `connected`; the LED buttons light the red, green and blue LED; **Status** prints the boot counters.
The tag goes to deep sleep about 10 s after power-up if nothing connects, so connect right after it wakes up.
