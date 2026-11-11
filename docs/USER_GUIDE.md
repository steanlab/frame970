# frame970: user guide

Own firmware for the Hanshow Nebular Pro 970Q-N (960 x 672, black / white / red / yellow). The tag shows pictures you upload from the
control page (Web Bluetooth, Chrome or Edge on Android or a computer) or from any OpenDisplay client. This guide covers what you see and
do with the tag; the byte-level description is in `PROTOCOL.md`, colours in `COLOUR.md`, hardware in `HARDWARE.md`.

The control page is in Russian; its card names are given in quotes. This guide is a first version and is extended with the firmware.

The card "Светодиод" on the page switches the LED colours by hand for testing (about 20 s); it has nothing to do with the signals below.

## The name of the tag

The tag advertises as `OD-xxxx`, where `xxxx` are the last two bytes of its Bluetooth address (for example `OD-96C1`). The `OD-` prefix
is fixed: OpenDisplay clients look for it. On the control page (card "OpenDisplay", field "имя метки") you can replace the four
digits by your own text of up to 5 characters, for example `OD-Milan`. Eight characters is all that fits into the advertisement.
"Reset" brings the default name back. The name is stored in the tag and survives battery changes.

If your browser does not list the tag in the device chooser, tick "показать все устройства" before pressing "Connect".

## The LED

The tag has one RGB LED. It is only used for short signals, so it hardly uses any battery. The mode is chosen on the control page
(card "Состояние", field "светодиод") and stored in the tag:

* **all events** (default),
* **boot, errors and low battery only**,
* **off**.

| Signal | Colour and pattern | When | Mode |
|---|---|---|---|
| Boot | red, green, blue, red, green, blue (about 1 s) | the tag starts: battery inserted, reset, reboot command, watchdog reset | all, errors-only |
| Connected | one short blue flash | a phone or computer connects | all |
| Receiving a picture | one short blue flash per second | an upload is running (the page, or an OpenDisplay client) | all |
| Picture shown | two green flashes | the panel finished refreshing (the picture is on) | all |
| Slide change | short yellow flash | the slideshow starts to draw the next slide | all |
| Error | three red flashes | upload failed (CRC, timeout, connection lost, flash), the panel did not answer | all, errors-only |
| Low battery | five quick red flashes | the supply voltage is critical (below 2.5 V): at power-up, at every slide change and every 10 minutes while the tag is awake | all, errors-only |

Wake-ups between slides (a few seconds every minute while the slideshow waits) are silent.

## Status: battery and temperature

The card "Состояние" (Status) of the control page shows, every 30 seconds while connected:

* **Supply voltage.** The tag has a 3.0 V lithium cell. Above 2.7 V is normal, below 2.7 V is "low", below 2.5 V is "critical" (red LED flashes).
  The tag also shows the lowest voltage seen during the last panel refresh: the refresh is the heaviest load, so a big difference to the idle
  voltage means a tired cell. The measurement is not calibrated, expect about 5 % error. OpenDisplay clients get the same voltage from the
  advertisement.
* **Panel temperature.** The panel has its own sensor, read at every refresh (the picture waveform depends on it). "Measure panel temperature"
  powers the panel for about a second and reads it now. The value shows how long ago it was measured. After a deep sleep or a reboot it is
  empty until the next measurement.
* **Chip sensor (raw value).** The processor has its own temperature sensor. The manufacturer gives no conversion to degrees, so the page shows the
  raw reading only. It is useful to see changes, not absolute values.

## Language of the control page

The control page speaks Russian and English. The buttons RU / EN in the top right corner switch the language; the choice is remembered in
the browser. By default the page follows the browser language (Russian, Belarusian and Ukrainian browsers get Russian, all others English).

## Other settings (card "Система")

* **Radio power**: +10 dBm (longest range, more current) down to -19 dBm (only at arm's length). Default +3 dBm.
* **Watchdog**: restarts the tag if the firmware hangs for more than 15 s. Default on. Switch it off only when testing.
* **Reboot tag**: restarts the tag (the boot signal shows it). OpenDisplay clients can reboot it with their reboot command as well.
