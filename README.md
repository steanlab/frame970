# frame970

Own firmware, a web control page and hardware documentation for the **Hanshow Nebular Pro 970Q-N**: a 9.7" electronic shelf label with a
960 x 672 black / white / red / yellow e-paper panel and a Telink TLSR8258 Bluetooth LE chip.
With this firmware the tag shows pictures that you send from a browser (Web Bluetooth) or from an OpenDisplay client, keeps up to four of them in its flash
and can change them on a timer, on a battery that lasts for months. The 437Q-N is planned next.

**Control page:** <https://steanlab.github.io/frame970/> (Chrome or Edge on a computer or Android; installable as an app; works offline after the first visit; Russian and English)

> **Release candidate 0.9.0-rc1.** It is tested on one tag. Flashing **replaces the original firmware** of the tag, so back up the stock flash first
> ([`firmware/FLASHING.md`](firmware/FLASHING.md)). Use at your own risk, no warranty.
> Unofficial: not affiliated with Hanshow, Telink, OpenDisplay or OpenEPaperLink.
> The Bluetooth link has **no authentication**: anyone in radio range can change the picture.

## What it does

- **Pictures from the page.** Pick an image, the page converts it to the four panel colours (colour-calibrated, with dithering in linear light), and uploads it over Bluetooth into one of 4 slots. The panel refresh itself takes about 20 s at room temperature and up to about 40 s when it is cool.
- **Slideshow.** Slots are shown in turn every 1 to 1080 minutes. Between slides the tag is in deep sleep (a few microamps) and wakes every few seconds for a short connect window.
- **Ghost clean-up.** A clean cycle (white, or black then white) removes the remnants of earlier pictures; it can run before every n-th slide.
- **OpenDisplay compatible.** The tag advertises as `OD-xxxx` and answers the OpenDisplay direct-write protocol. Checked with the uploader on opendisplay.org (orientation and colours correct). Other clients are untested.
- **Status.** Supply voltage (idle and lowest during the last refresh), panel temperature, raw reading of the chip's temperature sensor, firmware version.
- **LED signals** for boot, connection, upload, done, error and low battery (see the user guide). Can be reduced or switched off.
- **Settings stored in the tag:** own name tail (`OD-Milan`), radio power, watchdog, LED mode, slideshow.
- **The page checks the firmware version** and warns when page and firmware do not match.

The page keeps the rarely needed and the dangerous things (NFC chip writes, raw panel commands, pin scans) in two collapsed blocks, **Advanced** and **For developers**.

Not done yet: NFC tap action (the NFC chip is only probed), over-the-air firmware update, encryption / PIN, battery and refresh-time optimisation (the V300 queue of the author), the 437Q-N.

## Documents

| File | What |
|---|---|
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) ([Русский](docs/USER_GUIDE.ru.md)) | using the tag and the page: name, LED signals, battery, temperature, settings |
| [`firmware/FLASHING.md`](firmware/FLASHING.md) | what to back up and check before you flash, how to flash, how to go back |
| [`docs/HARDWARE.md`](docs/HARDWARE.md) | everything known about the board: chips, pins, LED, UART, NFC, battery, flash map, panel bus protocol, drawing sequence, timings, with the certainty of each fact |
| [`docs/PROTOCOL.md`](docs/PROTOCOL.md) | the Bluetooth protocol (own commands and the OpenDisplay layer) |
| [`docs/COLOUR.md`](docs/COLOUR.md) | measured panel colours |
| [`NOTICE.md`](NOTICE.md) | provenance, third-party licences, what is deliberately not published |

## Repository

| Path | What |
|---|---|
| `docs/index.html` | the control page (GitHub Pages) and the installable-app files (`manifest.json`, `sw.js`, icons) |
| `docs/tools/` | Pico (MicroPython) scripts to sniff and drive the panel, a PNG converter, and an extractor that finds the panel waveforms in **your own** flash dump |
| `firmware/` | the release-candidate binary with its SHA-256 sum, and the flashing guide |

## Licence and sources

The page, the documents and the tools are under the MIT licence ([`LICENSE`](LICENSE)). The firmware file may be used on your own tags without any warranty.
**The firmware source code is not published.** Third-party licences, provenance and the Telink SDK note: [`NOTICE.md`](NOTICE.md).
The panel waveform tables are factory data of every tag and are **not** published here: the firmware reads them from the tag itself, and `docs/tools/extract_waveforms.py` shows you how to read yours.

Questions and results from other tags are welcome in the Issues (please do not post MAC addresses, flash IDs or flash dumps). A similar project for another tag: [badge154](https://github.com/steanlab/badge154).
