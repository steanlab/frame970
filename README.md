# frame970

Control page and hardware documentation for the **Hanshow Nebular Pro 970Q-N** (9.7", 960 x 672, black / white / red / yellow e-paper tag, Telink TLSR8258)
running its own firmware. The 437Q-N is planned next.

**Control page:** https://steanlab.github.io/frame970/ (Chrome or Edge, desktop or Android; installable as an app, works offline after the first visit)

> **Work in progress.** The firmware is at the test stage: Bluetooth link, deep sleep, LED and NFC probing. Image upload and the slideshow are not there yet.
> Flashing **replaces the original firmware** of the tag. Back up the stock flash first. Use at your own risk, no warranty.
> Unofficial: not affiliated with Hanshow, Telink or OpenEPaperLink.

## What works now

- The page connects to a tag advertising as `n970-XXXXXX` (GATT service / characteristic `0x2446`, the OpenDisplay-style layout) and shows the tag's log, sent as Bluetooth notifications.
- Test commands: LED colours, NFC scan / read / pin watch, status, deep sleep with timer wake-up, auto-sleep, raw hex.
- Panel: the full drawing sequence, the pin map and the waveform records are documented and verified from a Raspberry Pi Pico ([`docs/HARDWARE.md`](docs/HARDWARE.md)). Drawing from the tag's own firmware is not done yet.

## Plan

1. Slide storage in the tag's flash and a slideshow by timer and NFC tap.
2. OpenDisplay-compatible protocol and image upload from the page.
3. One firmware code base for the 970Q-N and the 437Q-N.
4. Colour and white-level tuning (white currently looks grey on this panel).

## Repository

| Path | What |
|---|---|
| `docs/index.html` | the control page (GitHub Pages) and the installable-app files (`manifest.json`, `sw.js`, icons) |
| [`docs/HARDWARE.md`](docs/HARDWARE.md) | what is known about the board and the panel: pins, bus protocol, drawing sequence, waveforms, stock firmware map, and how sure each fact is |
| `docs/waveforms/` | the 14 waveform records of one tag (`.md` description and `.bin`) |
| `docs/tools/` | Pico (MicroPython) scripts used to sniff and drive the panel, and a waveform extractor |
| [`firmware/FLASHING.md`](firmware/FLASHING.md) | the test firmware file and what to know before flashing it |
| `firmware/` | the test firmware file with its SHA-256 sum |

## Licence and sources

The page and the documents are under the MIT licence ([`LICENSE`](LICENSE)). The firmware file is free to use on your own tags, without any warranty.
**The source code of the firmware is not published.** Third-party licences and provenance: [`NOTICE.md`](NOTICE.md).
Questions and results from other tags are welcome in the Issues. A similar project for another tag: [badge154](https://github.com/steanlab/badge154).
