# frame970 BLE protocol (firmware 5b)

Service `0x2446`, one characteristic `0x2446` (write, write without response, notify).
Device name `n970-AABBCC`. The first byte of a write is the command. The tag answers with text lines
(`\n` terminated, split into 20-byte notifications); the web page joins them.

This is a working protocol of the project. OpenDisplay compatibility (firmware 5e) works on top of it, see the last section.

## Slide storage

Four slots (0..3) in the tag's flash, 0x28000 bytes each from 0x30000. A slot holds one raw frame of
161 280 bytes and, in its last 256 bytes, a header that is written only after the data was read back
and its CRC matched. An erased or half-written slot therefore never looks valid.

Frame format: the panel's native scan order, 672 lines of 960 pixels, 2 bits per pixel, 4 pixels per byte, the first
pixel in bits 7..6. Colour index: 0 white, 1 black, 2 red, 3 yellow. Scan line `y` is column `y` of the portrait picture
(672 wide, 960 high), scan pixel `x` is portrait row `x`. The firmware turns the indices into the two panel passes while it draws.

## Commands

| bytes | meaning |
|---|---|
| `40` | list slots: `slot 0: 161280 bytes crc=XXXXXXXX` or `slot 0: empty` |
| `41 ss` | erase slot `ss` (`FF` = all) |
| `42 ss len32 crc32 win` | begin upload (32-bit values little endian, CRC-32 as zlib). Erases the slot, then answers `UP READY chunk=C win=W mtu=M rx=R` |
| `43 seq16 data...` | one chunk of `C` bytes at offset `seq*C` (seq little endian, from 0); the last one may be shorter. The tag answers `UP ACK n` after every `W` chunks and after the last one (`n` = bytes stored so far); the sender waits for it before the next window |
| `44` | end: the tag checks length and CRC, reads the slot back, writes the header, answers `UP OK slot s crc=XXXXXXXX` |
| `45 ss` | draw slot `ss` on the panel (about 30 s; log lines `epd: ...`, last one `epd: done`) |
| `46 ss` | write the built-in test picture into slot `ss` |
| `47 ss` | re-read slot `ss` and check its CRC |
| `48` | `LINK mtu=.. dle tx=.. rx=..`: the negotiated ATT MTU and link packet sizes |
| `49` | abort an upload |
| `4A en every16 mask poll [clean mode]` | slideshow settings: `en` 0/1, `every` minutes (little endian, 1..1080), `mask` slots in bits 0..3, `poll` seconds between wake-ups (10..250), optional `clean` = clean the panel before every n-th slide (0 = never) and `mode` 1 = white, 2 = black then white. Stored in flash. Answers with the `SS ...` line |
| `4B` | report the slideshow: `SS on every=60 mask=0F poll=30 clean=0/1 last=1 el=120` (minutes, slot mask, seconds, clean n/mode, last slot shown, seconds elapsed) |
| `4C` | draw the next slide now |
| `4D mode slot` | OpenDisplay stream orientation (0..3) and target slot (0..3); replies `OD mode=.. slot=..` |

Any error during an upload gives `UP FAIL reason` and cancels it (wrong sequence number, bad CRC, 30 s without data, disconnect).
`C` is chosen by the tag: `min(MTU-6, link rx size-10, 240)`, so a whole ATT write always fits one link packet.

## Slideshow

With the slideshow on, the tag sleeps (deep sleep, a few microamps) and wakes every `poll` seconds. Each wake-up opens a connect window of about
6 s; when the interval has passed the tag draws the next filled slot of the mask, then sleeps again. At power-up it draws a slide right away
after a 10 s window. The elapsed time is counted from the sleep times, so the interval is accurate to a few percent only. With the slideshow
off the tag stays awake and connectable. The settings are an append-only log of 8-byte records in flash sector 0xF7000.

## Older commands

`01 nn` deep sleep nn s, `02` status, `04 nn` auto-sleep, `10 11` LED, `20..2B` NFC discovery, `30..33` panel test (see the page), `34 mode` clean the panel against ghost images (1 = white, 2 = black then white, about 1 to 2 minutes).

## OpenDisplay compatibility (firmware 5e)

Same service and characteristic `0x2446`. OpenDisplay commands are a 2-byte big-endian opcode with high byte `00`;
ours start with `01`..`4D`, so the two never clash. Replies are notifications `00 cmd ...` (ok) or `FF cmd ...` (error).
While an OpenDisplay client is talking (any write that starts with `00`) the firmware sends no text log lines; a write that does not
start with `00` switches the text log back on.

The tag advertises manufacturer data with company id `0x2446` (14 bytes, zeros at the moment: no battery, temperature or button data)
and, in the scan response, the service `0x2446` and the name `OD970-AABBCC` (OpenDisplay clients look for names that start with `OD`).

| opcode | meaning | reply |
|---|---|---|
| `00 43` | firmware version | `00 43 major minor len text`, here 1 0 7 `n970-5e` |
| `00 40` | read configuration | chunks `00 40 nnnn data`; chunk 0 is `00 40 0000 total16 data`, up to 96 data bytes per chunk |
| `00 44` | manufacturer data | `00 44` + `46 24` + 14 bytes |
| `00 50` | authenticate | `00 50 03` (encryption is not configured) |
| `00 70` | direct write start (no size field: no compression) | `00 70` after the slot has been erased (a few seconds) |
| `00 71 data` | up to 230 bytes of the stream | `00 71` per chunk, `FF 71` on an error |
| `00 72 [mode] [etag]` | end: verify, commit, draw | `00 72`, then `00 73` when the panel is done (`00 74` if it fails) |
| anything else | | `FF cmd` (config write, reboot, DFU and so on are not supported) |

Configuration (packets `01` system, `02` manufacturer, `04` power, `20` display, CRC-16/CCITT-FALSE) says: 960 x 672 pixels,
colour scheme 3 (black, white, red, yellow), transmission mode direct write, no partial update. `ic_type` is 5 (nRF52811) because that is the
closest feature set in the list; the Telink chip is not in it. Panel size in millimetres and the panel IC are 0 (unknown).

**Pixels.** 2 bits per pixel, 4 pixels per byte, leftmost pixel in bits 7..6, black 0, white 1, yellow 2, red 3, line after line,
960 pixels per line, 672 lines: exactly the scan order of our slot frames, so the stream is written to flash on the fly (colour index xor 1).
The panel scans the picture transposed, so a landscape picture needs a flip to look right on the tag. The firmware does it while it stores the stream,
chosen by `4D mode slot`: mode bit 0 reverses the order of the lines, bit 1 the order of the pixels inside a line
(1 and 2 are the two 90 degree turns, 0 and 3 give mirrored pictures). The default is mode 1, slot 3; the values are kept in the settings record.
The `rotation` field of the configuration reports 1 for mode 1 and 3 for mode 2, the direction a client has to turn a picture before it sends it;
which of the two a given client expects has to be tried (change it with `4D`, then read the configuration again).
The stream replaces the content of the chosen slot and is drawn right after `00 72`.
