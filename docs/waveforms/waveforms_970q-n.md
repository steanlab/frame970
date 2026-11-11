# Nebular Pro 970Q-N waveform records

Panel waveform data used by the stock firmware, read from the tag flash at `0xF8188` (stride `0x21F`, 14 records) of one Hanshow Nebular Pro 970Q-N.
The same 528-byte tables also appear in third-party firmware for this tag. They are published for interoperability, with no warranty. They come from one
tag and one panel batch: where possible read the tables from your own tag (see `README_hardware_Nebular-970Q-N.md`, "Where the waveforms come from") instead of
copying these. The data carries no tag-specific identifiers; the 8 trailing bytes are the same in all records.

## Files

- `waveforms_970q-n.bin` - the 14 records back to back, 14 x 543 = 7602 bytes, exactly as stored in the flash.

## Record layout (543 bytes)

| Bytes | Content |
|---|---|
| 0..6 | parameters p0..p6 (sent as shown in the drawing sequence: `CMD 01 | 07 p0 p1 p3 p2 p4`, `CMD 30 | p6`, `CMD 82 | p5 + 0x80`, and the first 7 bytes of `CMD 20`) |
| 7..534 | 528 waveform bytes (the rest of `CMD 20`) |
| 535..542 | `06 00 06 04 0F 8B 93 C1` in every record; the last four are the data of `CMD 06` |

Record index = 2 * temperature band + pass: even = long drive (pass 0), odd = short drive (pass 1).

| Band | Temperature (C) | Long record | Short record |
|---|---|---|---|
| 0 | <= 9 | 0 | 1 |
| 1 | <= 12 | 2 | 3 |
| 2 | <= 15 | 4 | 5 |
| 3 | <= 20 | 6 | 7 |
| 4 | <= 25 | 8 | 9 |
| 5 | <= 30 | 10 | 11 |
| 6 | > 30 | 12 | 13 |

Parameters of the records:

| Record | Band | Pass | p0..p6 |
|---|---|---|---|
| 0 | 0 | long (0) | `00 26 78 2c 1b 24 02` |
| 1 | 0 | short (1) | `00 14 78 14 14 24 02` |
| 2 | 1 | long (0) | `00 23 78 2a 23 24 02` |
| 3 | 1 | short (1) | `00 14 78 14 14 24 02` |
| 4 | 2 | long (0) | `00 25 78 2d 1e 18 02` |
| 5 | 2 | short (1) | `00 14 78 14 14 18 02` |
| 6 | 3 | long (0) | `00 2b 78 32 2b 18 02` |
| 7 | 3 | short (1) | `00 14 78 14 14 18 02` |
| 8 | 4 | long (0) | `00 25 78 28 25 18 02` |
| 9 | 4 | short (1) | `00 14 78 14 14 18 02` |
| 10 | 5 | long (0) | `00 28 78 2c 28 24 02` |
| 11 | 5 | short (1) | `00 14 78 14 14 24 02` |
| 12 | 6 | long (0) | `00 1d 78 2a 1d 20 02` |
| 13 | 6 | short (1) | `00 14 78 14 14 24 03` |

## Python: split the file

```python
d = open("waveforms_970q-n.bin", "rb").read()
recs = [d[i*543:(i+1)*543] for i in range(14)]
band = next(i for i, t in enumerate((9, 12, 15, 20, 25, 30, 127)) if temp_c <= t)
rec = recs[2 * band + pass_no]
params, wave = rec[:7], rec[7:535]
# CMD 20 data = params + wave (535 bytes)
```

## Hex dump of the 528 waveform bytes

### Record 0 (band 0, long, pass 0)

```
  0: ef 7f ff ff ff 35 7f 76 76 ff 7f ef 7f ff 7f bd ef ed bd 7f ef 7e ef 7f
 24: ff 7f 7f ff 76 f2 ff ff ef ef 7f ff af ff ff 00 be b3 3c ef ef 7f ff af
 48: ef ff ef ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef df de 10 ff 37 ef ff
 96: ff ff ef ef de de 7f bd ef ed bd 7f ef 7e ef de fe 7f 7f ff 76 ef 6c 6e
120: ef ef f2 9d ef 3f ad 7e af bf 6e 7d fd d6 ff ef f7 ff ef be ff ff ef bf
144: 9d ff ef ef 75 ef ec ff ff ef ef f4 9d 6e 76 ef 7f 6f ff af ef ef ff ff
168: fd ff ff ef ff ff ff ff ef fb de 8b ff 28 ef ff ff ff ef ef de de 7f bd
192: ef ed bd 7f ef 7e ef de ff 7f 7f ff 76 ef ff ff ef ef de df 6d 7f 7f 2d
216: af 7d ff bd ef ff ff 5a af ff ef 6f ff ff 00 ef f7 f7 73 ec 2f ef fc 6f
240: ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef fb de bf ff f8 ef 76 76 ff 7f ef de de 7f bd ef ed bd 7f ef 7e ef de
288: ff 7f 7f ff 76 00 04 6c ef ef 9d 9d ed 75 2d bf 7f 34 b4 af ef df fd 7d
312: 2d af 7f 2f aa 7d ef ef f7 ff ae 6f ff ef ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef d7 de 00 a7 ff ef ff
360: ff ff ef ef de de 7f bd ef ed bd 7f ef 7e ef de ff 7f 7f ff 76 ef 6c 6e
384: ef ef f2 b5 ef 2f bd 7e af bf 6e 7d fd d6 ff ef f5 7f ef 7d ff ff ef bf
408: d6 f6 ef 3c ed ef ef 7d 7e ef ef 94 99 ef 2c 3c ef fa 7d bf ef ff ff ff
432: ff ff ff ff ff ff ff ff ef ff ff ff ff 35 7f 76 76 ff 7f ef ff ff 7f bd
456: ef ed bd 7f ef 7e ef ff ba 7f 7f ff 76 ef 00 20 ef ef fb ff 2e 00 20 ef
480: ff ff ff ff ef ff ff df 20 20 ef e8 ff ff ef ef ff bf be b3 3c ef df 7f
504: bf ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 1 (band 0, short, pass 1)

```
  0: ef 7f ff e7 ed 3f ef 7e 2f fe ef ef 7f ff 3e 7d 7d ef ff ff ff ef ff 7f
 24: ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff
 48: ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef d5 b3 3c 7d 3d ef 2d
 96: 3d bf ef ef bb fb ed 7e ed ef fd ff ff ef ff ff ff ff ff ff ff ff ff ff
120: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
144: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
168: ff ff ff ff ff ff ff ff ef ff ff e7 ed fe ef fd 2f fe ef ef ff ff 7f be
192: be ef ff ff ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
216: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
240: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef f9 ff af 37 7e ef 3f 3f fe ef ef f3 ff 3f 3d 3e ef ff ff ff ef ff ff
288: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
312: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef de d7 7d ad a5 ef 7d
360: 2d ef ef ef f3 ff fd ed af ef 2d ff ff ef ff ff ff ff ff ff ff ff ff ff
384: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
408: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
432: ff ff ff ff ff ff ff ff ef be ba e7 ed fe ef fd 2f fe ef ef ba ff 7f bf
456: b7 ef ff ff ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
480: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
504: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 2 (band 1, long, pass 0)

```
  0: ef 7f ff ff ff af 7f 76 76 ff 6f ef 7f ff 7f 7f ff f6 f3 ff ff ef ef 7f
 24: ff 7f 7f ff f5 f2 67 ff ef ef 7f ff bf ff ff 00 be b4 3c ef ef 7f ff af
 48: ef ff ef ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef d7 de 00 77 ae ef ff
 96: ff ff ef 7f de de 6f 2f 7f 3f 2f 6f 7f 3f ef de fe 7f 7f ff f5 ef 6c 6e
120: ef ef f2 9d ef 3f ad 7e bf af 6e af fd d6 ff ef 3c ff ef 3e ff ff ef bf
144: 9d ff ef ef 3c ef 2d ff ff ef ef f4 d6 3f f5 ef 7f 7f bf fc ef ff ff ff
168: ff ff ff ff ff ff ff ff ef fb de fb ff 35 ef 76 76 ff 7f 7f de de 6f 2f
192: 7f 3f 2f 6f 7f 3f ef de fe 7f 7f ff f5 ef 6c 6f ef ef de df 7d 7f 6f ad
216: fd 2f ff bd ef ff ff 69 05 ef ef 7f ff ff 00 ef f7 df b3 2f bf ef af ff
240: ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef df de 29 ff 2c ef 76 76 ff 7f 7f de de 6f 2f 7f 3f 2f 6f 7f 3f ef de
288: ff 7f 7f ff f5 00 58 ff ef ef 9d 9d bf bd bd fd ef a7 76 af ef df fd af
312: ef ff af f5 76 fd ef ef ff ff 7e ff ff ef ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef d7 de 00 26 ff ef ff
360: ff ff ef 7f de de 6f 2f 7f 3f 2f 6f 7f 3f ef de fe 7f 7f ff f5 ef 6c 6e
384: ef ef f2 b5 ef fd 6d 7e bf af 6e af fd 94 ff ef be 7d ef 3e ff ff ef bf
408: 94 ff ef be 6d ef 2f ff ff ef ef 99 d2 3c b4 76 ef 7d 3f ff ef ff ff ff
432: ff ff ff ff ff ff ff ff ef ff ff ff ff af 7f 76 76 ff 6f ef ff ff 7f 7f
456: ff f6 f3 ff ff ef ef ff ba 7f 7f ff f5 ef 00 20 ef ef fb ff 2e 00 20 ef
480: ff ff ff ff ef ff ff df 20 25 ef ab ff ff ef ef ff bf be b4 3c ef 2f ef
504: 3f ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 3 (band 1, short, pass 1)

```
  0: ef 7f ff 77 ed fe ef ee 67 af ef ef 7f ff ed ad ed ef 7d ef ff ef ff 7f
 24: ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff
 48: ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef f5 de 2c 6f 3d ef 3d
 96: ef ef af ef bb ba 7d bf bf ef af 7f bf ef ef fb ff ef ff ff ef ff ff ff
120: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
144: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
168: ff ff ff ff ff ff ff ff ef ff ff 77 ed fe ef ee 67 af ef ef ff ff ed ad
192: ed ef 7d ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
216: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
240: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef f5 ff a7 7d 2f ef ee 67 ed ef ef f9 ff fd ee 2f ef 7d ef ff ef ff ff
288: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
312: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef fe de 77 7d 3f ef 6d
360: ef af af ef f9 ff af bf 3f ef fd ff ff ef ff ff ff ff ff ff ff ff ff ff
384: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
408: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
432: ff ff ff ff ff ff ff ff ef be ba 77 ed fe ef ee 67 af ef ef ba ba ed ad
456: ed ef 7d ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
480: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
504: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 4 (band 2, long, pass 0)

```
  0: ef 7f ff ff ff ec 7f 76 76 ff 7f ef 7f ff 7f bd ef ed bd 7f ef 7e ef 7f
 24: ff 7f 7f ff 76 f2 ff ff ef ef 7f ff af ff ff 00 be b3 3c ef ef 7f ff af
 48: ef ff ef ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef df de 92 ff 3f ef ff
 96: ff ff ef ef de de 7f bd ef ed bd 7f ef 7e ef de fe 7f 7f ff 76 ef 6c 6e
120: ef ef f2 9d ef 3f ad 7e af bf 6e 7d fd d6 ff ef 3c ff ef 3e ff ff ef bf
144: 9d ff ef ef a7 ef 3c ff ff ef ef f4 d6 ed b4 ef 7f 6f bf ed ef ff ff ff
168: ff ff ff ff ff ff ff ff ef fb de 0b ff 66 ef ff ff ff ef ef de de 7f bd
192: ef ed bd 7f ef 7e ef de ff 7f 7f ff 76 ef ff ff ef ef de df 6d 7f 7f 2d
216: af 7d ff bd ef ff ff 5a af ff ef 6f ff ff 00 ef f7 f7 32 ec 2f ef bf 6f
240: ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef fb de 22 ff 2c ef 76 76 ff ef ef de de 7f bd ef ed bd 7f ef 7e ef de
288: ff 7f 7f ff 76 00 58 ff ef ef 9d 9d fd 7d 7d fd 6f 63 3c af ef df fd 67
312: ec ff ef ff e1 ee ef ef df ff 6f ef ff ef ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef df de 50 ff ff ef ff
360: ff ff ef ef de de 7f bd ef ed bd 7f ef 7e ef de ff 7f 7f ff 76 ef 6c 6e
384: ef ef f2 b5 ef 2f bd 7e 7f 6f 2e 7d fd d6 ff ef 3c ff ef 3e ff ff ef bf
408: d6 d6 ef 3c fd ef ef 6e 7d ef ef bd d2 7d b3 3c ef bd bf ff ef ff ff ff
432: ff ff ff ff ff ff ff ff ef ff ff ff ff ec 7f 76 76 ff 7f ef ff ff 7f bd
456: ef ed bd 7f ef 7e ef ff ba 7f 7f ff 76 ef 00 20 ef ef fb ff 2e 00 20 ef
480: ff ff ff ff ef ff ff df 20 20 ef e8 ff ff ef ef ff bf be b3 3c ef df 7f
504: bf ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 5 (band 2, short, pass 1)

```
  0: ef 7f ff 77 ed fe ef ee 67 af ef ef 7f ff ed ad ed ef 7d ef ff ef ff 7f
 24: ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff
 48: ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef f5 de 2c 6f 3d ef 3d
 96: ef ef af ef bb ba 7d bf bf ef af 7f bf ef ef fb ff ef ff ff ef ff ff ff
120: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
144: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
168: ff ff ff ff ff ff ff ff ef ff ff 77 ed fe ef ee 67 af ef ef ff ff ed ad
192: ed ef 7d ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
216: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
240: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef f5 ff a7 ad 3f ef ee 67 fd ef ef f9 ff fd 7e af ef 7d ef ff ef ff ff
288: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
312: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef fe de 2c 6d 3f ef 7d
360: ef af af ef fb f7 ef fd 6d ef ff 7f fd ef ff ff ff ff ff ff ff ff ff ff
384: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
408: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
432: ff ff ff ff ff ff ff ff ef be ba 77 ed fe ef ee 67 af ef ef ba ba ed ad
456: ed ef 7d ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
480: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
504: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 6 (band 3, long, pass 0)

```
  0: ef 7f ff ef ff ff 00 3b ff ff ef ef 7f ff 7f 7f ff f6 f3 ff ff ef ef 7f
 24: ff 7f 7f ff 3c f2 67 ff ef ef 7f ff bf ff ff 00 be b4 3c ef ef 7f ff af
 48: ef ff ef ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef f7 df ff ef ff 00 bd
 96: 74 ff ef 7f de de 6f 2f 7f 3f 2f 6f 7f 3f ef de ff 7f 7f ff 3c ef 6c 6e
120: ef ef f2 9d ef 3f ad 7e bf af 6e af fd d6 ff ef 3c ff ef 3e ff ff ef bf
144: 9d ff ef ff 3c ef fd ff ff ef ef d2 d6 7d bd b0 ef 3f ef 6f ef ff ff ff
168: ff ff ff ff ff ff ff ff ef ff fb ff ff ff ff ba c2 ff ef 7f de de 6f 3f
192: 6f 3f 2f 6f 7f 3f ef de fe 7f 7f ff 3c ef 6c 6f ef ef de df 7d 7f 6f ad
216: fd 2f ff bd ef ff ff 69 05 ef ef 7f ff ff 00 ef f7 d7 33 ef 3f ef af 7f
240: ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef ff df ef ff ff 00 64 6d ff ef 7f de de 6f 2f 7f 3f 2f 6f 7f 3f ef de
288: ff 7f 7f ff 3c 00 58 ff ef ef 9d 9d bf bd bd fd ef b6 67 af ef df fd af
312: ef ff af f5 74 7d ef ef ff ff fd ff ff ef ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef f7 df ff ef ff 00 3b
360: ff ff ef 7f de de 6f 2f 7f 3f 2f 6f 7f 3f ef de ff 7f 7f ff 3c ef 6c 6e
384: ef ef f2 9d ef 3f ad 7e bf af 6e af fd d6 ff ef 3c ff ef 3e ff ff ef bf
408: 9d ff ef ff f7 ef 3f ff ff ef ef d2 d2 7d 31 3c ef af ef ff ef ff ff ff
432: ff ff ff ff ff ff ff ff ef ff ff ef ff ff 00 3b ff ff ef ef ff ff 7f 7f
456: ff f6 f3 ff ff ef ef ff ba 7f 7f ff 3c ef 00 20 ef ef fb ff 2e 00 20 ef
480: ff ff ff ff ef ff ff df 20 25 ef ab ff ff ef ef ff bf be b4 3c ef af ef
504: fd ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 7 (band 3, short, pass 1)

```
  0: ef 7f ff e7 ed 3f ef 7e 2f fe ef ef 7f ff 3e 7d 7d ef ff ff ff ef ff 7f
 24: ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff
 48: ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef d5 b3 3c 7d 3d ef 2d
 96: 3d bf ef ef bb fb ed 7e ed ef fd ff ff ef ff ff ff ff ff ff ff ff ff ff
120: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
144: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
168: ff ff ff ff ff ff ff ff ef ff ff e7 ed fe ef fd 2f fe ef ef ff ff 7f be
192: be ef ff ff ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
216: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
240: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef f9 ff af 37 7e ef 3f 3f fe ef ef f3 ff 3f 3d 3e ef ff ff ff ef ff ff
288: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
312: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef de d7 ed af 25 ef 3d
360: 7d bf ef ef f3 ff 3d 3f 2f ef 2d ff ff ef ff ff ff ff ff ff ff ff ff ff
384: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
408: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
432: ff ff ff ff ff ff ff ff ef be ba e7 ed fe ef fd 2f fe ef ef ba ff 7f bf
456: b7 ef ff ff ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
480: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
504: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 8 (band 4, long, pass 0)

```
  0: ef 7f ff ff ff 6e 7f 76 76 ff ef 7f 7f ff 7f ef 7f 2f af ef ff 6f ef 7f
 24: ff bf af 6f 3f 6f 6f ef be fd 7f ff 7f 7f ef ef 2d ee ef ef 2f 7f ff af
 48: fe 6f ef ef 7f ef ef ef 7f ff 7f bf ef ef af fe af ef ef 7f ff 6f 3f bf
 72: ef ef 3f 7f ef ff 7f ff ff ff ff ff ff ff ff ff ef df de f3 ff 75 ef ff
 96: ff ff ef 7f f9 df 7f ef 7f 2f af ef ff 6f ef f9 de bf af 6f 3f 6f 6f ef
120: be fd de d2 7f 7f ef ef bd 3d 2f ef 2f f7 db 7f ef ef ef 6d bf ed ef ef
144: d6 ff 7f 6f fe ef 3f 6f 6f ef ef 99 b5 7f 3f 6f ef 3f 7f 7f ef ef ff ff
168: ef ff ff ef ff ff ff ff ef fb de e4 ff ea ef ff ff ff ef 7f f9 df 7f ef
192: 7f 2f af ef ff 6f ef f9 de bf af 6f 3f 6f 6f ef be fd de de 7f 7f ef ef
216: 6d 6f 6e ef 2f ff de ef 7f ef ef af ef 7e ef ef ff dd ef fe ef ef 3f af
240: bf ef ef fd fd 6f 3f bf ef 7f 3f ef ef ff ff ff ff ff ff ff ff ff ff ff
264: ef df de fe ff 3e ef 76 76 ff ef 7f f9 df 7f ef 7f 2f af ef ff 6f ef f9
288: de bf af 6f 3f 6f 6f ef be fd de f6 7f 7f ef ef 3d 3d af ef 2f f7 f6 ef
312: 7f ef ef 2f af bd ef ef f7 ff 7f 6d 3f ef af bf af ef ef ff ff 6f 3f bf
336: ef af 7f 7f ef ff ff ff ff ff ff ff ff ff ff ff ef df de 5d ff ff ef ff
360: ff ff ef 7f f9 df 7f ef 7f 2f af ef ff 6f ef f9 de bf af 6f 3f 6f 6f ef
384: be fd de d2 7f 7f ef ef bd 3d 2f ef 2f f5 db 7f ef ef ef be ef 6f ef ef
408: f4 99 7f 2d ef ef ed ef af ef ef db 90 6f 3f bf ef bf 7f 6f ef ff ff ff
432: ff ff ff ff ff ff ff ff ef ff ff ff ff 6e 7f 76 76 ff ef 7f ff ff 7f ef
456: 7f 2f af ef ff 6f ef ff ff bf af 6f 3f 6f 6f ef be fd ff ba 7f 7f ef ef
480: 2d ee ef ef 2f bf fa ef 7f ef ef af fe 6f ef ef ff ba ef fe ef ef 3f bf
504: af ef ef ba ff 6f 3f bf ef 3f 7f ef ef ff ff ff ff ff ff ff ff ff ff ff
```

### Record 9 (band 4, short, pass 1)

```
  0: ef 7f ff 77 ed fe ef ee 67 af ef ef 7f ff ed ad ed ef 7d ef ff ef ff 7f
 24: ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff
 48: ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef ff de e7 ed fd ef ed
 96: ef 3f af ef bb b9 6f ad 6f ef 6f af ef ef ff ff ff ff ff ff ff ff ff ff
120: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
144: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
168: ff ff ff ff ff ff ff ff ef ff ff 77 ed fe ef ee 67 af ef ef ff ff ed ad
192: ed ef 7d ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
216: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
240: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef f5 ff 66 3f 7f ef ee 67 af ef ef f9 ff bf be 3f ef 6d ef ff ef ff ff
288: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
312: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef f7 ff 75 6e 7d ef af
360: 67 af ef ef f9 ff 2f 3e 7f ef 6d ff ff ef ff ff ff ff ff ff ff ff ff ff
384: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
408: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
432: ff ff ff ff ff ff ff ff ef ba ba 77 ed fe ef ee 67 af ef ef ba ba ed ad
456: ed ef 7d ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
480: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
504: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 10 (band 5, long, pass 0)

```
  0: ef 7f ff ff ff 3d 7f 76 76 ff ef 7f 7f ff 7f af ef 6f af 7f ef 6f ef 7f
 24: ff 7f 7f ef 3c 7d 63 ff ef ef 7f ff 00 87 ff ef be be 3f ef ef 7f ff af
 48: ef ff ef ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef df de 71 ff 3e ef ff
 96: ff ff ef 7f de de 7f af ef 6f af 7f ef 6f ef de be 7f 7f ef 3c 7f ed 7f
120: af ef ff b5 ef 6f af 7e 7f fd 7e 6f 6f d6 ff ef be 7f ef 7f ff ff ef 6f
144: d6 ff ef be fd ef 7d ff ff ef ef db d6 af 7d fe ef bf bf e7 ef ef ff ff
168: 3f ff ff ef ff ff ff ff ef fb de af ff 2e ef 76 76 ff ef 7f de de 7f af
192: ef 6f af 7f ef 6f ef de fe 7f 7f ef 3c 6f 6c 6f ef ef de de 6f ef ef bd
216: ed 7f bf af ef df ff af ff 7d bf ef 7f bd ef ef fd fd d9 6a 7f ef e5 3f
240: 3f ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef df de 2d ff ad ef 76 76 ff ef 7f de de 7f af ef 6f af 7f ef 6f ef de
288: f6 7f 7f ef 3c 6f 6c 2f ef ef ff 9d ef 6f 2f 7e fd bf 7d bf ef 9d df 7f
312: bd 3e bf 7f ef 6f af ef fd fd bf 3c af ef ed e7 6f ef ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef df de 20 ff ef ef ff
360: ff ff ef 7f de de 7f af ef 6f af 7f ef 6f ef de b7 7f 7f ef 3c 7f ed 7f
384: af ef f2 b5 ef 6f af 7e af 6f 7e 6f 6f b5 ff ff ef 3c ef ef ff ff ef 6f
408: d6 ff ef be 7d ef ef af bf ef ef f6 db ef 6e fe ef 2d 3f ff ef ff ff ff
432: ff ff ff ff ff ff ff ff ef ff ff ff ff 3d 7f 76 76 ff ef 7f ff ff 7f af
456: ef 6f af 7f ef 6f ef ff ba 7f 7f ef 3c 6f 87 a7 ef ef fb ff 2e 00 ff ef
480: ff ff ff ff ef ff ff ff af ff ef ed ff ff ef ef ff bf be be ff ef fd ff
504: b7 ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 11 (band 5, short, pass 1)

```
  0: ef 7f ff 77 ed fe ef ee 67 af ef ef 7f ff ed ad ed ef 7d ef ff ef ff 7f
 24: ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff
 48: ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef f7 de 65 af ff ef 3d
 96: ef ef af ef fb bb 7d 3f ff ef bf ef 3f ef ef ff ff ef ef ef ef ff ff ff
120: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
144: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
168: ff ff ff ff ff ff ff ff ef ff ff 77 ed fe ef ee 67 af ef ef ff ff ed ad
192: ed ef 7d ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
216: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
240: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef fc ff b5 6f ad ef ee 67 bf ef ef f9 ff bf 3e fd ef 2f ef ff ef ff ff
288: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
312: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef fc ff b5 ef ae ef 2d
360: 3c ef ef ef f9 ff 2f 3e 6f ef ad ef ff ef ff ff ff ff ff ff ff ff ff ff
384: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
408: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
432: ff ff ff ff ff ff ff ff ef be ba 3c ad fe ef ee 67 af ef ef ba ba ed ad
456: ed ef 7d ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
480: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
504: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 12 (band 6, long, pass 0)

```
  0: ef 7f ff ff ff 2e 7f ff ff ff ff 7f 7f ff 7f af ef 3f af 7f ef fd ef 7f
 24: ff ef ef ff fa bc d5 ff ef ef 7f ff 7f ff ff 00 be be 3c ef ef 7f ff af
 48: ef ff ef ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef fb de bf ff 75 ef ff
 96: ff ff ef 7f de de 7f af ef 3f af 7f ef fd ef de b7 ef ef ff fa ef 3d 7f
120: 3f ef ff 9d ef 7f fe fe bf bf be 6f 6f d6 ff ef ed 6d ef bd ff ff ef 6f
144: d6 ff ef bd ae ef af ff ff ef ef d6 9d ef be 2f ef 6f ff af ef ef ff ff
168: f5 ff ff ef ff ff ff ff ef fb de a7 ff ed ef ff ff ff ef 7f de de 7f af
192: ef 3f af 7f ef fd ef de fe ef ef ff fa ef 6c 7f ef ef de b7 6f ef ef 3c
216: ed 7d ef 3f ef df ff be ef e6 ef ef 00 f5 ef ef f7 fd 76 af 36 ef 6f ff
240: bf ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef df de ff ff 35 ef ff ff ff ef 7f de de 7f af ef 3f af 7f ef fd ef de
288: b6 ef ef ff fa b8 7d ef bf ef 9d d6 7f bd fd bf 7f 7f ff af ef df db af
312: b4 3d ef 2f f3 bd ef ef dd ff 6f 34 6f ef ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef df de a5 ff ef ef ff
360: ff ff ef 7f de de 7f af ef 3f af 7f ef fd ef de b7 ef ef ff fa ef 3d 7f
384: 3f ef f2 b5 ef 6f 2d fe af af 7e af bf d6 fe ef fe 3f ef fd ef 7d ef ef
408: d6 fb ef 7e 6f ef ef af ff ef ef de 90 7f ef 3d ef fd 7d af ef ff ff ff
432: ff ff ff ff ff ff ff ff ef ff ff ff ff 2e 7f ff ff ff ff 7f ff ff 7f af
456: ef 3f af 7f ef fd ef ff ba ef ef ff fa ef 00 30 ef ef fb ff 2e 00 ff ef
480: ff ff ff ff ef ff ff bd ff ee ef ed fd ff ef ef ff bf fd fe 2e ef bf be
504: af ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```

### Record 13 (band 6, short, pass 1)

```
  0: ef 7f ff ec 2d be ef 2f af ef ef ef 7f ff ef ef ef ef ef ef ef ef ff 7f
 24: ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff
 48: ff ff ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ff 7f ff ff ff ff
 72: ff ff ff ff ff ff 7f ff ff ff ff ff ff ff ff ff ef f5 df 6d 3f 3f ef bd
 96: ff ff 7f ef ff fe ff 2f ff ef ff ee fd ef ff ff ff ff ff ff ff ff ff ff
120: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
144: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
168: ff ff ff ff ff ff ff ff ef ff ff 3d 6e fe ef 6f ef be ef ef ff ff ef ef
192: 6f ef ff ef ff ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
216: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
240: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
264: ef fd ff f5 6d fd ef 7f 6f ef ef ef f3 ff af 2f ef ef ff ef ff ef ff ff
288: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
312: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
336: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ef fc 9f 75 6f 6d ef ed
360: ef 6f ef ef f3 ff 6f bf ef ef 7f ff ff ef ff ff ff ff ff ff ff ff ff ff
384: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
408: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
432: ff ff ff ff ff ff ff ff ef be ba ee be be ef 7d af ef ef ef ba ba ef ef
456: ef ef ef ef ef ef ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
480: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
504: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
```
