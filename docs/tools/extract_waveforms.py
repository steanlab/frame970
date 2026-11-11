#!/usr/bin/env python3
"""Find the factory waveform block in a full flash dump of a Nebular Pro 970Q-N and write the 14 waveform records.

Usage: extract_waveforms.py flash_dump.bin [out.bin]
The block is 0x3000 bytes; its first two bytes (little endian) are the CRC16 of the remaining 0x2FFE bytes (poly 0x1021, init 0x1D0F, no final XOR).
The records start 0x188 bytes into the block, stride 0x21F bytes, 14 records (7 temperature bands x {long, short}).
Prints only the address and the record parameters. The rest of the block is tag-specific factory data: do not publish it.
"""
import sys
def crc16(data, c=0x1D0F):
    for b in data:
        c ^= b << 8
        for _ in range(8): c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c
d = open(sys.argv[1], 'rb').read()
found = [off for off in range(0, len(d) - 0x3000 + 1, 0x100) if int.from_bytes(d[off:off + 2], 'little') == crc16(d[off + 2:off + 0x3000])]
if not found: raise SystemExit('no CRC-valid 0x3000 block found')
base = found[0]; print('waveform block at 0x%X' % base)
recs = [d[base + 0x188 + i * 0x21F: base + 0x188 + (i + 1) * 0x21F] for i in range(14)]
for i, r in enumerate(recs):
    print('record %2d band %d %-5s params %s trailing %s' % (i, i // 2, 'long' if i % 2 == 0 else 'short', r[:7].hex(' '), r[535:].hex(' ')))
if len(sys.argv) > 2:
    open(sys.argv[2], 'wb').write(b''.join(recs)); print('wrote', sys.argv[2])
