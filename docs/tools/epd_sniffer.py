# SPI sniffer for an e-paper panel on a Raspberry Pi Pico (MicroPython + PIO).
# Listens to CS / CK / SDA / DC (SPI mode 0 or 3, MSB first, 8 bits per byte), plus RST and BUSY, and prints what the tag says to the panel:
# every command (DC low) with the first 4095 data bytes after it. Later data bytes of long runs (pixels) are not kept.
# Wiring (Pico GP number -> tag pad):  GP10 SDA, GP11 CK, GP12 CS, GP13 DC, GP14 BUSY, GP15 RST, and GND to the tag's GND pad. Nothing else.
# Use: run this file in Thonny, THEN switch the tag on (battery in). Stop with Ctrl-C (or it stops itself 20 s after the last event).
import time
import rp2
from machine import Pin
import micropython

PIN_SDA, PIN_CK, PIN_CS, PIN_DC, PIN_BUSY, PIN_RST = 10, 11, 12, 13, 14, 15
SAMPLE_ON_RISING = True      # SPI modes 0 and 3. If the output is garbage, set False (modes 1 and 2).
IDLE_STOP_S = 20             # stop after this many seconds without any event
CHUNK_IT = 2_000_000         # loop iterations per capture() call (about half a second)
KEEP = 4095                  # data bytes kept after each command (the PIO program below builds this number: twelve 1-bits)


# Program for the PIO. in_base = SDA, so wait/in "pin 0" = SDA, "pin 1" = CK, "pin 2" = CS; jmp_pin = DC.
# Per byte: wait until CS is low, shift in 8 bits on the sampling edge of CK. DC high = data byte: push it while the counter x lasts
# (x is reloaded with 4095 by every command), then drop it. DC low = command: push it inverted (so it is always >= 0xFFFFFF00;
# data words are < 0x100) and reload x. A push that finds the FIFO full is dropped (noblock): the PIO never stalls.
@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT, autopush=False, fifo_join=rp2.PIO.JOIN_RX)
def sniff_rise():
    wait(0, pin, 2)
    set(y, 7)
    label("bit")
    wait(0, pin, 1)
    wait(1, pin, 1)
    in_(pins, 1)
    jmp(y_dec, "bit")
    jmp(pin, "data")
    mov(isr, invert(isr))
    push(noblock)
    mov(x, invert(null))
    in_(x, 12)
    mov(x, isr)
    mov(isr, null)
    jmp("start")
    label("data")
    jmp(not_x, "drop")
    jmp(x_dec, "store")
    label("store")
    push(noblock)
    jmp("start")
    label("drop")
    mov(isr, null)
    label("start")
    nop()


@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT, autopush=False, fifo_join=rp2.PIO.JOIN_RX)
def sniff_fall():
    wait(0, pin, 2)
    set(y, 7)
    label("bit")
    wait(1, pin, 1)
    wait(0, pin, 1)
    in_(pins, 1)
    jmp(y_dec, "bit")
    jmp(pin, "data")
    mov(isr, invert(isr))
    push(noblock)
    mov(x, invert(null))
    in_(x, 12)
    mov(x, isr)
    mov(isr, null)
    jmp("start")
    label("data")
    jmp(not_x, "drop")
    jmp(x_dec, "store")
    label("store")
    push(noblock)
    jmp("start")
    label("drop")
    mov(isr, null)
    label("start")
    nop()


# Capture loop in viper (native speed): the PIO RX FIFO is only 8 words deep, so the CPU must never be slow.
# Entries are pairs of words in buf: (word, loop iteration number). word < 0x100 = data byte, >= 0xFFFFFF00 = command (inverted),
# 0x1000 | (BUSY) | (RST << 1) = a BUSY/RST change. Returns after max_it iterations once the FIFO is empty and things are quiet,
# so the Python code between calls only runs while the bus is silent. Registers: PIO0 FSTAT 0x50200004 (bit 8 = RX empty of SM0),
# PIO0 RXF0 0x50200020, SIO GPIO_IN 0xD0000004.
@micropython.viper
def capture(buf: ptr32, cap: int, st: ptr32, max_it: int, pb: int, pr: int, pc: int) -> int:
    fstat = ptr32(0x50200004)
    rxf = ptr32(0x50200020)
    gpio = ptr32(0xD0000004)
    n = int(st[0])
    it = int(st[1])
    last = int(st[2])
    lastev = int(st[3])
    cs = int(st[4])
    pend = int(st[5])
    end_it = it + max_it
    while n + 2 <= cap:
        if ((int(fstat[0]) >> 8) & 1) == 0:
            buf[n] = rxf[0]
            buf[n + 1] = it
            n += 2
            lastev = it
        else:
            g = int(gpio[0])
            p = ((g >> pb) & 1) | (((g >> pr) & 1) << 1)
            c = (g >> pc) & 1
            if p != last:
                last = p
                buf[n] = 0x1000 | p
                buf[n + 1] = it
                n += 2
                lastev = it
            elif c != cs:
                cs = c
                lastev = it
                if c == 1:
                    pend = it                 # CS rose: maybe the end of a burst, decided 3000 iterations later
                elif pend >= 0:
                    pend = -1                 # CS fell again soon: same burst (CS toggles per byte)
                else:
                    buf[n] = 0x2001           # CS fell after a pause: start of a new burst
                    buf[n + 1] = it
                    n += 2
            elif it >= end_it and (it - lastev) > 4000:
                it += 1
                break
        if pend >= 0 and (it - pend) > 3000 and cs == 1 and n + 2 <= cap:
            buf[n] = 0x2000                   # the burst really ended when CS rose
            buf[n + 1] = pend
            n += 2
            pend = -1
        it += 1
    st[0] = n
    st[1] = it
    st[2] = last
    st[3] = lastev
    st[4] = cs
    st[5] = pend
    return n


class Log:
    """Turns (time_us, word) pairs into readable lines."""
    def __init__(self):
        self.ev = []          # [kind, t_us, value, data_bytes]
        self.cur = None

    def word(self, w, t):
        if w < 0x100:
            if self.cur is not None:
                self.cur[3].append(w)
                self.cur[4] = t
            else:
                self.ev.append(["data?", t, w, [], t])
        elif w >= 0xFFFFFF00:
            self.cur = ["cmd", t, (~w) & 0xFF, [], t]
            self.ev.append(self.cur)
        elif (w & 0xF000) == 0x1000:
            self.pins(w, t)
        elif w == 0x2000:
            self.ev.append(["cs", t, 1, [], t])
        elif w == 0x2001:
            self.ev.append(["cs", t, 0, [], t])

    def pins(self, w, t):
        p = w & 3
        b, r = p & 1, (p >> 1) & 1
        if getattr(self, "pb", None) != b:
            self.pb = b
            self.ev.append(["busy", t, b, [], t])
        if getattr(self, "pr", None) != r:
            self.pr = r
            self.ev.append(["rst", t, r, [], t])

    def lines(self):
        out = []
        t0 = self.ev[0][1] if self.ev else 0
        for kind, t, v, d, tl in self.ev:
            head = "%10.3f ms  " % ((t - t0) / 1000.0)
            if kind == "cmd":
                if d:
                    dur = (tl - t) / 1000.0
                    out.append(head + "CMD %02X  data(%d%s) kept bytes took %.3f ms (%.1f us/byte):" % (v, len(d), "+" if len(d) >= KEEP else "", dur, (tl - t) / len(d)))
                    for i in range(0, len(d), 24):
                        out.append("                " + " ".join("%02X" % b for b in d[i:i + 24]))
                else:
                    out.append(head + "CMD %02X" % v)
            elif kind == "data?":
                out.append(head + "data byte %02X before any command" % v)
            elif kind == "cs":
                out.append(head + ("CS low (burst starts)" if v == 0 else "CS high (burst ends)"))
            else:
                out.append(head + "%s -> %d" % (kind.upper(), v))
        return out


def alloc():
    import array
    for words in (28000, 16000, 8000, 4000):
        try:
            return array.array("I", bytes(4 * words)), words
        except MemoryError:
            pass
    raise MemoryError("no memory for the capture buffer")


def decode(buf, chunks, log):
    """chunks: (n0, n1, it0, it1, ta_us, tb_us) per capture() call -> feed log in time order."""
    for n0, n1, it0, it1, ta, tb in chunks:
        k = (tb - ta) / (it1 - it0) if it1 > it0 else 0
        for e in range(n0, n1, 2):
            log.word(buf[e], ta + (buf[e + 1] - it0) * k)


def run():
    import array
    for p in (PIN_SDA, PIN_CK, PIN_CS, PIN_DC, PIN_BUSY, PIN_RST):
        Pin(p, Pin.IN)
    prog = sniff_rise if SAMPLE_ON_RISING else sniff_fall
    sm = rp2.StateMachine(0, prog, freq=125_000_000, in_base=Pin(PIN_SDA), jmp_pin=Pin(PIN_DC))
    busy, rst = Pin(PIN_BUSY, Pin.IN), Pin(PIN_RST, Pin.IN)
    buf, cap = alloc()
    p0 = busy.value() | (rst.value() << 1)
    st = array.array("i", [0, 0, p0, 0, 1, -1])
    log = Log()
    log.pins(0x1000 | p0, 0)
    chunks = []
    print("start: BUSY=%d RST=%d. Now switch the tag on. Ctrl-C to stop (it also stops %d s after the last event)." % (p0 & 1, p0 >> 1, IDLE_STOP_S))
    T0 = time.ticks_us()
    sm.active(1)
    t_last = time.ticks_ms()
    full = False
    try:
        while True:
            n0, it0 = st[0], st[1]
            ta = time.ticks_diff(time.ticks_us(), T0)
            capture(buf, cap, st, CHUNK_IT, PIN_BUSY, PIN_RST, PIN_CS)
            tb = time.ticks_diff(time.ticks_us(), T0)
            chunks.append((n0, st[0], it0, st[1], ta, tb))
            if st[0] != n0:
                t_last = time.ticks_ms()
            if st[0] + 2 > cap:
                full = True
                break
            if len(log.ev) == 0 and st[0] == 0:
                pass
            if st[0] and time.ticks_diff(time.ticks_ms(), t_last) > IDLE_STOP_S * 1000:
                break
    except KeyboardInterrupt:
        pass
    sm.active(0)
    decode(buf, chunks, log)
    lines = log.lines()
    if full:
        lines.append("(capture buffer full - the end of the activity is missing)")
    print("---- begin log (%d events) ----" % len(log.ev))
    for s in lines:
        print(s)
    print("---- end log ----")
    try:
        with open("sniff.txt", "w") as f:
            f.write("\n".join(lines) + "\n")
        print("also saved to sniff.txt on the Pico")
    except OSError:
        pass


if __name__ == "__main__":
    run()
