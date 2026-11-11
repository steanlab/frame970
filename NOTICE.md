# Notice and provenance

frame970 is not affiliated with, or endorsed by, Hanshow, Telink, OpenEPaperLink or Solum. The names are used only to say which hardware the project works with.

## What is in this repository

The control page (`docs/index.html` and the installable-app files), the documents and the Pico scripts in `docs/tools/` were written for this project and are under the MIT licence (file `LICENSE`).
The repository also holds a compiled firmware file (release candidate 0.9.0-rc1). Its source code is **not** published.

## What the firmware file contains

The firmware is built on a pinned checkout of [atc1441/ATC_TLSR_Paper](https://github.com/atc1441/ATC_TLSR_Paper) (MIT licence, text in `firmware/ATC_TLSR_Paper-LICENSE.txt`):
the project's own files replace the application part, and the Telink SDK that the checkout ships (headers and the precompiled BLE library `liblt_8258.a`) is linked in.
Telink Semiconductor (Shanghai) Co., Ltd. holds the copyright of that SDK. The SDK file headers say that the information is available under a commercial licence agreement or
"free, non-transferable use ... under Mutual Non-Disclosure Agreement", with no warranty. The upstream project distributes the SDK sources and compiled firmware openly, as do other community
projects for these chips, but the licence terms were not reviewed by a lawyer. Whoever redistributes the binary does so on their own responsibility;
if Telink or the upstream author objects, the file will be removed.

## Where the hardware information came from

Pin assignments, the panel command sequence and the waveform locations were read from the stock firmware of the tag (flash dump of the author's own tag, taken with an external programmer),
by logic-level sniffing of the tag-to-panel bus, and then checked by driving the panel from a Raspberry Pi Pico and by running our own firmware. Details and the certainty of each fact are in `docs/HARDWARE.md`.
Register values, pin numbers, addresses and the layout of data blocks are facts about the hardware and are described there; no source code and no binary part of the stock firmware is published.

## What is deliberately not published

- **The panel waveform tables.** They are factory data stored in every tag's own flash (block `0xF8000`) and were first read from the stock firmware's data. Our firmware does not contain them: it reads the tables from the tag it runs on.
  `docs/HARDWARE.md` describes the block format, and `docs/tools/extract_waveforms.py` finds the block in a dump of your own tag.
- **Flash dumps, factory records, MAC addresses and unique flash IDs** of any tag.
- **The stock firmware** and the firmware source code.
