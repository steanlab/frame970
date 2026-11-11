# n970_otp_dump.py - read the 6144-byte block that the stock firmware reads from the 970Q-N panel (CMD 90, A0, 92) and save it to files.
# Read-only: it sends no picture and no waveform.
# Needs n970_pico_drive.py on the Pico (it is imported for the pin setup, the SPI sender and the panel reset). Same wiring as before.
# Usage: run in Thonny, insert the tag battery when it says so (same as before), wait for "finished".
# Result: otp_a.bin and otp_b.bin (6144 bytes each, two separate reads) on the Pico, plus CRC32 values and the first bytes in the Shell.
import time, binascii
import n970_pico_drive as d

N = 6144
READS = 2

def read_stream(n, delay_us=3):
    """Read n bytes with CS kept low, DC high (mode 0: sample SDA while CK is high)."""
    d.dc.value(1); d.sda.init(d.Pin.IN)
    ck, sda = d.ck, d.sda
    out = bytearray(n)
    for i in range(n):
        v = 0
        for _ in range(8):
            ck.value(0); time.sleep_us(delay_us); ck.value(1); time.sleep_us(delay_us)
            v = (v << 1) | sda.value()
        out[i] = v
    ck.value(0); d.sda.init(d.Pin.OUT); d.sda.value(0)
    return bytes(out)

def one_read():
    d.reset_panel()
    d.cs.value(0)                                    # CS stays low for the whole sequence, as the sniffer showed
    d.dc.value(0); d.send(b'\x90'); d.dc.value(1)
    d.wait_ready(timeout_s=5, settle_ms=1, name='after CMD 90')
    d.dc.value(0); d.send(b'\xA0'); d.dc.value(1)
    d.wait_ready(timeout_s=5, settle_ms=1, name='after CMD A0')
    d.dc.value(0); d.send(b'\x92'); d.dc.value(1)
    dummy = read_stream(1)
    data = read_stream(N)
    d.cs.value(1)
    return dummy, data

def main():
    if not d.START_NOW: d.wait_for_tag()
    print('taking over the lines'); d.own_lines()
    results = []
    try:
        for k in range(READS):
            print('read', k + 1, '...')
            dummy, data = one_read()
            name = 'otp_%s.bin' % 'ab'[k]
            with open(name, 'wb') as f: f.write(data)
            crc = binascii.crc32(data)
            print('  dummy byte %s, saved %s, %d bytes, CRC32 %08x' % (dummy.hex(), name, len(data), crc))
            print('  first 48 bytes:', data[:48].hex(' '))
            print('  distinct byte values:', len(set(data)), ' zeros:', sum(1 for x in data if x == 0), ' 0xFF:', sum(1 for x in data if x == 255))
            results.append(data)
            time.sleep(4)
        print('the two reads are', 'IDENTICAL' if len(results) == 2 and results[0] == results[1] else 'DIFFERENT')
        print('finished')
    finally:
        d.cs.value(1); d.release_lines()

if __name__ == '__main__':
    main()
