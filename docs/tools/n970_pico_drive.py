# n970_pico_drive.py - draw a picture on the Hanshow Nebular Pro 970Q-N panel (960 x 672, BWRY) from a Raspberry Pi Pico (MicroPython),
# while the tag's own MCU sleeps. Verified on hardware (see README_hardware_Nebular-970Q-N.md).
#
# Wiring:  GP10 SDA, GP11 CK, GP12 CS, GP13 DC, GP14 BUSY, GP15 RST, GND to the tag's GND pad (3.3 V logic, the tag is powered by its own battery).
# Files needed on the Pico (Thonny: View -> Files, right click -> Upload to /):
#   waveforms_970q-n.bin        14 records x 543 bytes (see waveforms/waveforms_970q-n.md, or extract_waveforms.py from a flash dump of your own tag)
#   picture_pass0.bin, picture_pass1.bin   161280 bytes each, made from a PNG by n970_frame.py
# Usage: run this file in Thonny, then insert the tag battery when it says so. The script waits until the tag has done its boot sequence and gone
# to sleep (no edges on CS/RST/BUSY for QUIET_S seconds), then takes over the lines. A full two-pass refresh takes about 35 s.
import time
from machine import Pin

PIN_SDA, PIN_CK, PIN_CS, PIN_DC, PIN_BUSY, PIN_RST = 10, 11, 12, 13, 14, 15
PICTURE_P0 = 'picture_pass0.bin'
PICTURE_P1 = 'picture_pass1.bin'
WAVEFORMS = 'waveforms_970q-n.bin'   # 14 records x 543 bytes: 7 parameter bytes + 528 waveform bytes + 8 trailing bytes
IDLE_START_S = 40                    # if no tag activity is seen for this long, assume it is already asleep and start
QUIET_S = 8                          # tag must be silent this long before we take over (its boot has a 3.3 s gap)
START_NOW = False                    # True: do not wait for the tag's boot cycle, start immediately (tag already asleep)
FORCE_BAND = None                    # None = choose by panel temperature; 0..6 to force a temperature band
PER_BYTE_CS = False                  # True: toggle CS around every byte (as the experimental firmware does)
BUSY_READY = 1                       # BUSY level when the panel is idle
BUSY_TIMEOUT_S = 20
PASS_GAP_S = 4                       # pause between the two passes (the stock firmware waits about 3.3 s after the panel went to sleep)
ONLY_PASS = None                     # None = both passes, 0 or 1 = only that pass (pass 1 alone only adds black on top of what is shown)
P1_LONG = False                      # True: use the long (even) waveform record also for pass 1
P1_REG50 = 0x97                      # CMD 50 data in pass 1 (pass 0 uses 0x37)
TRACE_MS = {0x12: 3000}              # longer BUSY trace after these commands (ms)
REFRESH_TIMEOUT_S = 120               # a 9.7 inch refresh takes much longer than 20 s
TRACE_CMDS = (0x04, 0x12, 0x02, 0x07, 0x20)   # after these commands print the BUSY changes of the next 10 ms
W, H, FRAME = 960, 672, 161280
THRESHOLDS = (9, 12, 15, 20, 25, 30, 127)

sda = Pin(PIN_SDA, Pin.IN); ck = Pin(PIN_CK, Pin.IN); cs = Pin(PIN_CS, Pin.IN)
dc = Pin(PIN_DC, Pin.IN); busy = Pin(PIN_BUSY, Pin.IN); rst = Pin(PIN_RST, Pin.IN)

try:
    import micropython
    @micropython.viper
    def _send(buf, n: int, sda_m: int, ck_m: int):
        p = ptr8(buf)
        st = ptr32(0xD0000014); cl = ptr32(0xD0000018)
        for i in range(n):
            b = int(p[i])
            for j in range(8):
                cl[0] = ck_m
                if b & 0x80:
                    st[0] = sda_m
                else:
                    cl[0] = sda_m
                st[0] = ck_m
                b <<= 1
except ImportError:
    _send = None

def send(buf, n=None):
    """Clock out bytes, MSB first, mode 0 (data valid on the rising edge of CK)."""
    n = len(buf) if n is None else n
    _send(buf, n, 1 << PIN_SDA, 1 << PIN_CK)

def own_lines():
    for p in (sda, ck, cs, dc, rst):
        p.init(Pin.OUT)
    cs.value(1); ck.value(0); dc.value(1); sda.value(0); rst.value(1)

def release_lines():
    for p in (sda, ck, cs, dc, rst):
        p.init(Pin.IN)

def wait_ready(timeout_s=BUSY_TIMEOUT_S, settle_ms=10, name=''):
    time.sleep_ms(settle_ms)
    t0 = time.ticks_ms(); was_busy = busy.value() != BUSY_READY
    while busy.value() != BUSY_READY:
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_s * 1000:
            raise RuntimeError('BUSY timeout')
        time.sleep_ms(1)
    print('  wait %s: BUSY was %s, waited %d ms' % (name, 'low' if was_busy else 'already ready', time.ticks_diff(time.ticks_ms(), t0)))

def cmd(c, data=b''):
    """One command byte (DC low) followed by data bytes (DC high)."""
    cs.value(0); dc.value(0); send(bytes([c])); dc.value(1)
    if PER_BYTE_CS:
        cs.value(1)
        for b in data:
            cs.value(0); send(bytes([b])); cs.value(1)
    else:
        if data: send(data)
        cs.value(1)
    if c in TRACE_CMDS:
        print('  CMD %02X sent, BUSY (us, level):' % c, busy_trace(TRACE_MS.get(c, 10)))

def cmd_stream(c, f, total):
    """Command followed by `total` data bytes read from an open file in chunks."""
    cs.value(0); dc.value(0); send(bytes([c])); dc.value(1)
    buf = bytearray(1024); left = total
    while left:
        n = f.readinto(buf) if left >= 1024 else f.readinto(memoryview(buf)[:left])
        if not n: raise RuntimeError('picture file too short')
        send(buf, n); left -= n
    cs.value(1)

def read_bytes(n, mode=0):
    """Read n bytes from the panel (DC high, SDA is an input). mode 0: sample while CK is high, mode 1: sample after CK falls."""
    cs.value(0); dc.value(1)
    sda.init(Pin.IN); out = []
    for _ in range(n):
        v = 0
        for _ in range(8):
            ck.value(0); time.sleep_us(3); ck.value(1); time.sleep_us(3)
            if mode == 0:
                bit = sda.value()
            else:
                ck.value(0); time.sleep_us(3); bit = sda.value()
            v = (v << 1) | bit
        out.append(v)
    ck.value(0); sda.init(Pin.OUT); sda.value(0); cs.value(1)
    return bytes(out)

def busy_trace(ms=30):
    """Sample BUSY for `ms` milliseconds and return the list of (time_us, level) changes."""
    t0 = time.ticks_us(); last = busy.value(); ev = [(0, last)]
    while time.ticks_diff(time.ticks_us(), t0) < ms * 1000:
        v = busy.value()
        if v != last:
            last = v; ev.append((time.ticks_diff(time.ticks_us(), t0), v))
    return ev

def read_temperature(verbose=True):
    """CMD 41 00, CMD 40, wait until BUSY is high again, then read 2 bytes in a separate CS burst (as the stock firmware does)."""
    cmd(0x41, b'\x00'); cmd(0x40)
    ev = busy_trace(30)
    if verbose: print('BUSY after CMD 40 (us, level):', ev)
    got = None
    for mode in (0, 1):
        t = read_bytes(2, mode)
        if verbose: print('read mode', mode, '->', t.hex(' '))
        if t[0] not in (0x00, 0xFF) and got is None: got = (t, mode)
    return got

def reset_panel():
    for lvl, ms in ((1, 20), (0, 20), (1, 200), (0, 20), (1, 20)):
        rst.value(lvl); time.sleep_ms(ms)

def band_for(temp_c):
    if temp_c > 127: temp_c -= 256
    for i, t in enumerate(THRESHOLDS):
        if temp_c <= t: return i
    return 6

def waveform_record(band, pas):
    with open(WAVEFORMS, 'rb') as f:
        f.seek((2 * band + pas) * 543); r = f.read(543)
    if len(r) != 543: raise RuntimeError('waveform file too short')
    return r

def run_pass(pas, picture, band):
    rec = waveform_record(band, 0 if (pas == 1 and P1_LONG) else pas); p = rec[:7]
    reset_panel()
    temp = read_temperature(verbose=False); wait_ready(name='after CMD 40')
    cmd(0x62, bytes((0x77, 0x77, 0x77, 0x5C, 0x9F, 0x8C, 0x77, 0x63)))
    cmd(0x00, b'\x27\xA8')
    cmd(0x01, bytes((0x07, p[0], p[1], p[3], p[2], p[4])))
    cmd(0x03, b'\x10\x54\x44')
    cmd(0x06, b'\x0F\x8B\x93\xC1')
    cmd(0x30, bytes((p[6],)))
    cmd(0x50, bytes((P1_REG50 if pas else 0x37,)))
    cmd(0x60, b'\x02\x02')
    cmd(0x61, bytes((W >> 8, W & 255, H >> 8, H & 255)))
    cmd(0x65, b'\x00\x00\x00\x00')
    cmd(0x82, bytes(((p[5] + 0x80) & 255,)))
    cmd(0xE3, b'\x22'); cmd(0xE7, b'\xC1'); cmd(0xE9, b'\x01')
    cmd(0x20, rec[:535])                       # 7 parameter bytes + 528 waveform bytes = 535
    with open(picture, 'rb') as f:
        cmd_stream(0x10, f, FRAME)
    cmd(0x04)
    wait_ready(name='after CMD 04 (power on)')
    cmd(0x12, b'\x00')
    wait_ready(timeout_s=REFRESH_TIMEOUT_S, settle_ms=100, name='after CMD 12 (refresh)')
    cmd(0x00, b'\x27\xA9'); cmd(0x02, b'\x00'); wait_ready(timeout_s=REFRESH_TIMEOUT_S, name='after CMD 02 (power off)')
    cmd(0x07, b'\xA5')
    return temp

def wait_for_tag():
    """Wait for the tag's boot cycle (edges on CS/RST/BUSY) and then for QUIET_S seconds of silence.
    If nothing happens for IDLE_START_S seconds the tag is assumed to be asleep already and we go on."""
    print('Insert the tag battery now (or leave it in if it is already inserted). Waiting up to %d s...' % IDLE_START_S)
    last = (cs.value(), rst.value(), busy.value()); edges = 0
    t_start = t_last = time.ticks_ms(); t_beat = t_start
    while True:
        now = time.ticks_ms()
        cur = (cs.value(), rst.value(), busy.value())
        if cur != last:
            edges += 1; last = cur; t_last = now
        elif edges >= 5 and time.ticks_diff(now, t_last) > QUIET_S * 1000:
            print('tag is quiet after %d edges' % edges); return
        elif edges < 5 and time.ticks_diff(now, t_start) > IDLE_START_S * 1000:
            print('only %d edges seen in %d s: assuming the tag is already asleep, going on' % (edges, IDLE_START_S)); return
        if time.ticks_diff(now, t_beat) > 3000:
            t_beat = now
            print('  waiting... edges=%d CS=%d RST=%d BUSY=%d' % (edges, cur[0], cur[1], cur[2]))
        time.sleep_ms(1)

def main():
    if not START_NOW: wait_for_tag()
    print('line levels after the tag went to sleep: CS', cs.value(), 'RST', rst.value(), 'BUSY', busy.value(), 'DC', dc.value(), 'CK', ck.value(), 'SDA', sda.value())
    print('taking over the lines'); own_lines()
    print('resetting the panel'); reset_panel()
    print('BUSY after our reset:', busy.value())
    got = read_temperature()
    if got is None:
        print('No sensible answer (all 00/FF). Look at the BUSY trace above: if BUSY never moved, the panel is probably not powered. Stopping.')
        release_lines(); return
    t, mode = got
    print('panel answered', t.hex(' '), 'using read mode', mode)
    temp = t[0]
    if temp > 127: temp -= 256
    if FORCE_BAND is None and not (-10 <= temp <= 45):
        print('temperature %d C is not plausible, using band 4 (20..25 C) instead' % temp)
        band = 4
    else:
        band = FORCE_BAND if FORCE_BAND is not None else band_for(temp)
    print('temperature', temp, 'C -> band', band)
    try:
        for pas, pic in ((0, PICTURE_P0), (1, PICTURE_P1)):
            if ONLY_PASS is not None and pas != ONLY_PASS: continue
            print('pass', pas, '...'); t0 = time.ticks_ms()
            run_pass(pas, pic, band)
            print('pass', pas, 'done in', time.ticks_diff(time.ticks_ms(), t0) // 1000, 's')
            if ONLY_PASS is None and pas == 0:
                print('waiting %d s before pass 1' % PASS_GAP_S); time.sleep(PASS_GAP_S)
        print('finished')
    except BaseException as e:
        print('stopped by', repr(e), '- sending the panel to sleep')
        try:
            cmd(0x02, b'\x00'); time.sleep_ms(500); cmd(0x07, b'\xA5')
        except BaseException:
            pass
        raise
    finally:
        release_lines()

if __name__ == '__main__':
    main()
