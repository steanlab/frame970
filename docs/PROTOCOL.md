# frame970 BLE protocol (firmware 5b)

Service `0x2446`, one characteristic `0x2446` (write, write without response, notify).
Device name `n970-AABBCC`. The first byte of a write is the command. The tag answers with text lines
(`\n` terminated, split into 20-byte notifications); the web page joins them.

This is a working protocol of the project. Compatibility with OpenDisplay is planned (step 6) and will be added on top, not instead.

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
| `4A en every16 mask poll` | slideshow settings: `en` 0/1, `every` minutes (little endian, 1..1080), `mask` slots in bits 0..3, `poll` seconds between wake-ups (10..250). Stored in flash. Answers with the `SS ...` line |
| `4B` | report the slideshow: `SS on every=60 min mask=0F poll=30 s last=1 elapsed=120 s` |
| `4C` | draw the next slide now |

Any error during an upload gives `UP FAIL reason` and cancels it (wrong sequence number, bad CRC, 30 s without data, disconnect).
`C` is chosen by the tag: `min(MTU-6, link rx size-10, 240)`, so a whole ATT write always fits one link packet.

## Slideshow

With the slideshow on, the tag sleeps (deep sleep, a few microamps) and wakes every `poll` seconds. Each wake-up opens a connect window of about
6 s; when the interval has passed the tag draws the next filled slot of the mask, then sleeps again. At power-up it draws a slide right away
after a 10 s window. The elapsed time is counted from the sleep times, so the interval is accurate to a few percent only. With the slideshow
off the tag stays awake and connectable. The settings are an append-only log of 8-byte records in flash sector 0xF7000.

## Older commands

`01 nn` deep sleep nn s, `02` status, `04 nn` auto-sleep, `10 11` LED, `20..2B` NFC discovery, `30..33` panel test (see the page).
