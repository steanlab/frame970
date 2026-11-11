# Hanshow Nebular Pro 970Q-N - hardware notes

Electronic shelf label with a 9.7" four-colour e-paper panel. These notes collect what is known about the board and the panel interface, so that
other developers can write their own firmware or drive the panel from another MCU. Everything here was found by reading the stock firmware, by
logic-level sniffing, and by driving the panel from a Raspberry Pi Pico. Items are marked **verified on hardware**, **from firmware analysis**
or **unknown**.

No per-tag data is published here: no UID / IDs and no factory record contents. The 14 waveform records of one tag are published separately in
`waveforms/waveforms_970q-n.md` and `waveforms/waveforms_970q-n.bin`; see "Where the waveforms come from" for how to read your own tag's tables.

## Overview

| | |
|---|---|
| Tag | Hanshow Nebular Pro 970Q-N |
| Display | 9.7" e-paper, 960 x 672, four colours: white, black, red, yellow (BWRY) |
| MCU | Telink TLSR8258 (TC32 core: ARM Thumb-1 with permuted opcode bits) |
| NFC | FM11NT083V (Fudan Micro) |
| External flash | 1 MiB dump read from a stock tag (stock firmware has 3 Telink images) |
| Panel interface | SPI-like bus (SDA, CK, CS) + DC, RST, BUSY. Register set similar to the UC81xx family |
| Stock panel type | model code 0x22 (34, "driver 34" in the strings), type index 10 |

The panel controller IC itself is not identified; the command set below is what the stock firmware sends for model 0x22.

## Pins (from firmware analysis)

Pin descriptors in the stock firmware are `(group << 8) | mask`. The tag's factory record selects between a hardware SPI mode and a bit-bang mode.
For the hardware SPI mode used by this tag the mapping is:

| Signal | MCU pin | Note |
|---|---|---|
| SDA (data out) | PB6 | measured with the pin-scan firmware (see below) |
| CK | PD7 | measured with the pin-scan firmware; same pin as the stock descriptor `0x380` |
| CS | PD2 | low across a whole command + its data; reads use a separate burst. Measured, 7 of 7 bursts |
| DC (data / command) | PB7 | low = command byte, high = data. Measured |
| RST | PD4 | measured; also fixed in the experimental firmware's code |
| BUSY | PA1 | high = ready, low = busy (verified on hardware; input only, the scan skips it) |
| Panel power | PB5 | active low (seen in third-party firmware code). Pulsing it in the pin scan made the BUSY line respond, which agrees with this, but the power switch itself was not probed directly |

**How the table was verified.** A small pin-scan firmware (source not published) drives every candidate GPIO with a burst of N pulses, N = table index + 1,
and a Raspberry Pi Pico on the panel lines counts the pulses per line. Result of one 45 s capture (about seven full scan cycles): SDA saw 13 pulses (PB6), CK 30 (PD7),
CS 25 (PD2), DC 14 (PB7), RST 27 (PD4). A burst occasionally came out 1 or 2 pulses short (a missed edge in the MicroPython listener, never one too many), which is why single bursts
sometimes name a neighbouring pin. The majority of the bursts on each line agree. CK also showed one stray burst of 13 (PB6) at the very start of the capture, which is not understood
and does not change the result. The BUSY line showed pulse counts of 12 and 14 most likely because the panel reacts when PB5 (power) or PB7 (DC) toggles; BUSY itself is driven by the panel, not by the MCU.

A bit-bang variant exists in the stock code (CS PB4, CK PB5, SDA PB6, DC PD7); it is selected by the factory record and is not used by this tag (the pin scan did not see PB4 on any panel line).
Because the pins come from the factory record, portable firmware should read the record at runtime instead of hard-coding them.

SDA is bidirectional: the panel answers reads (temperature, OTP block) on the same wire.

## Bus protocol (verified on hardware)

- SPI mode 0, MSB first. Bit-banging from a Pico worked; the stock tag uses hardware SPI.
- CS goes low before the command byte and stays low across the data bytes of that command, then goes high.
- Writes: DC low for the command byte, DC high for data bytes.
- Reads: DC high, clock the bits out and sample SDA while CK is high (mode 0 read).
- BUSY: high when the panel is idle. After most commands wait for BUSY to go high again (timeouts: 20 s normally, much longer for the refresh).

## Power-up and reset (verified)

Reset: RST high 20 ms, low 20 ms, high 200 ms, low 20 ms, high 20 ms.
After a tag cold boot the stock firmware runs its own init (about 22 s, with two resets and the OTP read) and then sleeps; the panel stays powered and
responds afterwards. A second MCU can take over the lines at that point; that is how all the Pico tests were done without removing the tag's MCU.

## Temperature (verified)

`CMD 41 | 00`, then `CMD 40`. BUSY goes low for about 4 ms. Wait until BUSY is high again, then read 2 bytes in a **separate CS burst**: byte 0 is the
temperature in degrees C (signed), byte 1 is a fraction (e.g. `18 00` = 24 C, `17 80` = 23.5 C). Reading in the same burst as `CMD 40` returns 00 00.

## Drawing a picture (verified on hardware)

One refresh is two passes: a long drive that sets the colours and a short one that deepens black. Each pass repeats the same register setup with a
different waveform record and pixel plane.

```
reset
CMD 41 | 00, CMD 40, wait BUSY high, read 2 bytes   (temperature -> band)
CMD 62 | 77 77 77 5C 9F 8C 77 63                    (960 x 672 set; other sizes use other 8-byte sets)
CMD 00 | 27 A8
CMD 01 | 07 p0 p1 p3 p2 p4                           (p0..p6 = parameter bytes of the waveform record)
CMD 03 | 10 54 44
CMD 06 | 0F 8B 93 C1
CMD 30 | p6
CMD 50 | 37 (pass 0)   97 (pass 1)
CMD 60 | 02 02
CMD 61 | 03 C0 02 A0                                 (width 960, height 672)
CMD 65 | 00 00 00 00
CMD 82 | p5 + 0x80
CMD E3 | 22     CMD E7 | C1     CMD E9 | 01
CMD 20 | p0..p6 + 528 waveform bytes                  (535 bytes)
CMD 10 | 161280 bytes of pixels                        (4 px per byte, first pixel in bits 7..6)
CMD 04                                                (panel power on), wait BUSY high
CMD 12 | 00                                            (refresh), wait BUSY high
CMD 00 | 27 A9, CMD 02 | 00 (power off), wait BUSY high, CMD 07 | A5 (deep sleep)
```

- Waveform record: pass 0 uses the **long** record, pass 1 the **short** record of the temperature band.
- Refresh time at 23-24 C: about 18 s for pass 0 and about 0.17 s for pass 1.
- Wait about 4 s between the two passes (the stock firmware waits about 3.3 s). Starting pass 1 right after pass 0 can leave the second refresh silently
  skipped.
- Running pass 1 alone on top of an existing image only adds black.

### Pixel values (2 bits, sent in `CMD 10`)

| Colour | pass 0 value | pass 1 value |
|---|---|---|
| white | 1 | 1 |
| black | 1 | 0 |
| red | 0 | 1 |
| yellow | 2 | 1 |

A single long pass can also draw all four colours with the values red 0, white 1, yellow 2, black 3, but black then comes out dark maroon.
The red pigment is brick red.

### Geometry

The scan buffer is 960 pixels per line x 672 lines. An upright image is 672 wide x 960 high (portrait): portrait pixel (px, py) = scan pixel (x = py, y = px).
Pixel (0,0) of a line is the first pixel (bits 7..6) of the first byte.

## Where the waveforms come from (from firmware analysis; checked against hardware results)

The waveforms are **not** in the firmware image; they are in the tag's own flash, in a factory-programmed block that the stock firmware reads. Do not
erase or overwrite it when you flash your own firmware, and keep a full backup of the flash before you start.

- Block address `0xF8000`, size `0x3000` (12 KiB).
- First two bytes: CRC16 of the remaining `0x2FFE` bytes (little endian). CRC: polynomial 0x1021, initial value 0x1D0F, MSB first, no final XOR.
  The stock firmware checks it with this value.
- The first `0x188` bytes are a header. Among other things it holds a table of **7 temperature ranges**, given in 1/100 C:
  up to 9 C, 12, 15, 20, 25, 30, and everything above (127 C). For each range the table holds two flash pointers (24-bit addresses): the long and
  the short waveform record.
- Records start at `0xF8188`, stride `0x21F` bytes (543). Each record is **7 parameter bytes + 528 waveform bytes + 8 more bytes**
  (the record length 0x21F also appears in the header table). The 8 trailing bytes are `06 00 06 04 0F 8B 93 C1` in every record; the last four are the data of `CMD 06`.
  The records themselves are in `waveforms/waveforms_970q-n.md` / `.bin`.
- Record order: temperature band 0 long, band 0 short, band 1 long, ... band 6 short (14 records).
- The meaning of the individual waveform bytes is not decoded; the panel accepts the 528 bytes unchanged in `CMD 20` (after the 7 parameter bytes).
- The rest of the block holds other factory data of the tag. Treat it as private: it is specific to each tag.

The panel also stores a block of its own which the stock firmware reads at boot: `CMD 90`, wait, `CMD A0`, wait, `CMD 92`, read one dummy byte,
then 6144 bytes (CS stays low through the whole sequence). The two reads were identical. The block starts with a 4-byte length (2274) and the packed data,
then zeros, an ASCII product/lot string and about 384 more bytes. The stock firmware logs "load wf over" / "unzip wf error" around it. This block is not
needed for drawing: the tag-side waveform table above is sufficient. Its format is not decoded.

## Stock firmware map (flash image offsets; the flash is mapped at 0)

| Address | What |
|---|---|
| 0x3b1e8 / 0x3b318 | send command byte (DC low) / send data byte (DC high) |
| 0x3b4e4 | wait for BUSY |
| 0x3b6b8 | reads the panel block (90 / A0 / 92 + 6144 bytes) |
| 0x3b780 / 0x3b820 | temperature read |
| 0x3b540 | model code (0x18..0x2d) to type index; 0x22 -> 10 |
| 0x3bb80 | init function for type 10 |
| 0x3c310 | refresh (`CMD 12 | 00`) |
| 0x3dc3c | deep sleep (`CMD 07 | A5`) |
| 0x3a444 | reset sequence |
| 0x2da0c | waveform block check (CRC16, 7 temperature ranges) |

Other `CMD 62` data sets that appear in the stock init (by panel geometry): 960x680 `76 76 76 5A 9D 8A 76 62`, 960x640 `7D 7D 7D 60 A7 93 7D 68`,
900x528 `98 98 98 75 CA B2 98 7E`.

## Reproducing the experiments

- A Raspberry Pi Pico wired to the panel lines (SDA, CK, CS, DC, RST, BUSY, GND) can drive the panel while the tag's MCU sleeps. Insert the battery, wait about
  25 s until the tag's own boot cycle has finished and the lines are quiet, then take over the lines. Release them again afterwards.
- Always end a run with `CMD 02 | 00` and `CMD 07 | A5` so the panel is not left powered with an image being driven.

## How this information was obtained

1. **Flash dump.** A full 1 MiB dump of the tag's flash, taken with an external SPI-flash programmer, was disassembled (TC32 is Thumb-1 with the top five
   opcode bits permuted; a small disassembler recovers it). The stock firmware logs "unzip wf" / "load wf over" around the waveform load; following the
   string references leads to the loader at `0x2D2D0` and its check function at `0x2DA0C`. That function copies a 392-byte header from a flash block and
   compares its first two bytes with a CRC16 (init `0x1D0F`, `0x2FFE` bytes). Scanning the dump for 0x3000-byte blocks whose CRC matches finds exactly one:
   `0xF8000`. `tools/extract_waveforms.py` repeats this scan on any dump and writes the 14 records.
2. **Sniffing the stock boot.** `tools/epd_sniffer.py` (Raspberry Pi Pico, MicroPython + PIO) records everything the tag sends to the panel: SDA, CK, CS, DC,
   RST and BUSY, decoded into commands and data. It showed the reset timing, `CMD 90 / A0 / 92` plus a 6 KB stream, and the temperature read.
3. **Driving the panel from the Pico.** `tools/n970_pico_drive.py` takes the lines over after the tag's own boot cycle has finished and draws a picture with the
   sequence above. `tools/n970_frame.py` converts a PNG to the two pixel streams. The colour values and the two-pass scheme in this file were established
   with this setup by trying the candidates and photographing the result.
4. **Reading the panel's own block.** `tools/n970_otp_dump.py` repeats the stock `90 / A0 / 92` read and saves the 6144 bytes (two reads, identical).
5. The waveform records found in the flash dump are byte-identical to the 14 tables embedded in a third-party firmware image for this tag; the panel
   draws correctly with them.

### Tools (all MicroPython scripts run on a Pico; the converters need Python 3 with Pillow)

| File | Purpose |
|---|---|
| `tools/epd_sniffer.py` | passive logger of the tag-to-panel traffic (Pico, PIO) |
| `tools/n970_pico_drive.py` | draw a picture on the panel from the Pico (needs `waveforms_970q-n.bin` and the two picture files on the Pico) |
| `tools/n970_otp_dump.py` | read the panel's 6144-byte block (needs `n970_pico_drive.py` next to it) |
| `tools/n970_frame.py` | PNG (672 x 960) -> `picture_pass0.bin` / `picture_pass1.bin` |
| `tools/extract_waveforms.py` | find the waveform block in a flash dump and write the 14 records |

Wiring for the Pico scripts: GP10 SDA, GP11 CK, GP12 CS, GP13 DC, GP14 BUSY, GP15 RST, plus GND. Solder to the panel lines on the tag board
(the lines are 3.3 V logic). Run the script in Thonny, insert the tag battery when it asks, wait for the tag's boot cycle to end (about 25 s), and the Pico
takes over. Quick start for a picture:

```
python3 tools/n970_frame.py my_portrait_672x960.png picture      # writes picture_pass0.bin, picture_pass1.bin
# upload picture_pass0.bin, picture_pass1.bin, waveforms_970q-n.bin and n970_pico_drive.py to the Pico, run n970_pico_drive.py
```

## Open questions

- Confirm CK = PD7 and SDA = PB6 with a real frame drawn by our own firmware (the pin scan only shows which pin is wired to which line).
- The panel driver IC, and the meaning of the waveform bytes (a custom, faster waveform would need this).
- How the NFC chip (FM11NT083V) is wired to the MCU and what the stock firmware does with it.
- The format of the panel's own 6144-byte block.
