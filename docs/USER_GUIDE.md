# frame970: user guide

Repo path: `steanlab/frame970` → `docs/USER_GUIDE.md` (Русская версия: [`USER_GUIDE.ru.md`](USER_GUIDE.ru.md))

Own firmware (0.9.0-rc1) for the Hanshow Nebular Pro 970Q-N (960 x 672, black / white / red / yellow). The tag shows pictures that you upload from the
control page (Web Bluetooth, Chrome or Edge on Android or a computer) or from an OpenDisplay client. This guide covers what you see and do with the tag.
Byte-level description: [`PROTOCOL.md`](PROTOCOL.md), colours: [`COLOUR.md`](COLOUR.md), hardware: [`HARDWARE.md`](HARDWARE.md), flashing: [`../firmware/FLASHING.md`](../firmware/FLASHING.md).

The control page is at <https://steanlab.github.io/frame970/>. Card names are given in quotes as they appear in English.

> The Bluetooth link has no authentication or encryption: anyone within radio range can change the picture and the settings.

## Language, firmware version

The buttons RU / EN in the top right corner switch the page language; the choice is remembered in the browser. By default the page follows the browser language
(Russian, Belarusian and Ukrainian browsers get Russian, all others English).

After connecting, the page reads the tag's firmware version and **protocol level** (footer: `page 0.9.0-rc1, protocol level 1 · tag firmware 0.9.0 (1)`).
If the levels differ, a warning banner tells which side is older: a tag with older firmware may not understand new buttons, an older cached copy of the page may not understand the tag.
Reload the page (it is installable and cached for offline use, so close the app once and open it again) or update the firmware.

## Connecting

Press "Connect" and choose `OD-xxxx` in the browser's list. If the list is empty, tick "show all devices" first.
With the slideshow on, the tag sleeps between short listening windows, so a connection may need a few seconds: the tag wakes every "poll" seconds (setting of the slideshow, 10 to 250 s).
Only one device can be connected at a time.

## The name of the tag

The tag advertises as `OD-xxxx`, where `xxxx` are the last two bytes of its Bluetooth address (for example `OD-96C1`). The `OD-` prefix is fixed: OpenDisplay clients look for it.
In the card "OpenDisplay" (field "tag name") you can replace the four digits by your own text of up to 5 characters, for example `OD-Milan`. Eight characters is all that fits into the advertisement.
"Reset" brings the default back. The name is stored in the tag and survives battery changes.

## Putting a picture on the tag

Card "Slides (tag flash)": the tag keeps four pictures (slots 0 to 3) in its flash.

1. Choose an image file. The page scales it to 672 x 960 (portrait): "fit" decides between filling (cropping), whole picture (white margins) and stretching; "rotation" turns it.
   If the tag hangs upside down, tick the "flip 180°" box (remembered).
2. The page reduces the picture to the four panel colours. "Palette: measured" uses the colours measured on this panel (a darker black, an orange-ish red) and dithers in linear light; "nominal" is the plain old behaviour. "Dither" is Floyd-Steinberg or none.
   The three calibration charts help to judge the result on your panel.
3. Pick a slot and press "Upload to slot". Progress is shown; "Abort" cancels. The mode "fast" is enough in most cases; "with confirmation" is slower and more tolerant of a bad link.
4. "Show on panel" draws the slot. The panel flickers for about 20 s at room temperature (up to about 40 s when cool), the LED flashes green twice at the end.
   Do not remove the battery or reconnect during a refresh.

Other buttons: "List" shows what is in the slots, "Verify CRC" re-reads a slot, "Erase" empties it, "Test picture to slot" writes a built-in pattern.

**Clean-up against ghost images.** E-paper keeps faint remnants of earlier pictures. "Clean-up ... white" paints the whole panel white (about a minute), "black, then white" first black, then white (about two minutes).
The slideshow can do it automatically (below).

## Slideshow

Card "Slideshow": tick the slots that should be shown, choose how often to change (1 to 1080 minutes) and press "Apply". The tag then sleeps in deep sleep (a few microamps by the chip's specification; not measured here)
and wakes every "poll" seconds to listen for a connection for a few seconds. When the interval has passed it draws the next slide and sleeps again. The interval is counted from the sleep times, so it is accurate to a few percent only.
"Clean the panel": never, before every slide, or every 3rd / 5th / 10th slide, white or black-then-white. "Next slide now" draws one at once; "Read from tag" shows the stored settings.
To change anything, connect at a wake-up and switch the slideshow off or change the settings; with the slideshow off the tag stays awake and connectable (and uses much more current).

## OpenDisplay clients

The tag also speaks the OpenDisplay direct-write protocol (the uploader on opendisplay.org was tested). It writes the picture into one slot (default slot 3) and draws it. Other OpenDisplay clients are untested.
The card "OpenDisplay" sets the slot and the orientation of the stream ("stream rotation": mode 1 or 2; try the other if the picture comes out rotated by 180°). The OpenDisplay clients also read the supply voltage from the advertisement.

## The LED

The tag has one RGB LED. It is used for short signals only, so it hardly uses any battery. The mode is chosen in the card "Status" (field "LED") and stored in the tag:
**all events** (default), **boot, errors and low battery only**, or **off**.

| Signal | Colour and pattern | When | Mode |
|---|---|---|---|
| Boot | red, green, blue, red, green, blue (about 1 s) | the tag starts: battery inserted, reset, reboot command, watchdog reset. Not shown after a wake-up from deep sleep | all, errors-only |
| Connected | one short blue flash | a phone or computer connects | all |
| Receiving a picture | one short blue flash per second | an upload is running (the page or an OpenDisplay client) | all |
| Picture shown | two green flashes | the panel finished refreshing | all |
| Slide change | short yellow flash | the slideshow starts to draw the next slide | all |
| Error | three red flashes | upload failed (CRC, timeout, connection lost, flash), the panel did not answer | all, errors-only |
| Low battery | five quick red flashes | supply voltage critical (below 2.5 V): at power-up, at every slide change and every 10 minutes while the tag is awake | all, errors-only |

Wake-ups between slides (a few seconds while the slideshow waits) are silent.

## Status: battery and temperature

The card "Status" shows, every 30 seconds while connected:

* **Supply voltage.** The tag has a 3.0 V lithium cell (the author's tag: EVE, 1450 mAh). Above 2.7 V is normal, below 2.7 V "low", below 2.5 V "critical" (red LED flashes).
  The tag also keeps the lowest voltage seen during the last panel refresh: the refresh is the heaviest load, so a big difference to the idle voltage means a tired cell.
  The measurement is not calibrated, expect about 5 % error. OpenDisplay clients get the idle voltage from the advertisement.
* **Panel temperature.** The panel has its own sensor, read at every refresh (the picture waveform depends on it). "Measure panel temperature" powers the panel for about a second and reads it now.
  The value shows how long ago it was measured; after a deep sleep or reboot it is empty until the next measurement.
* **Chip sensor (raw value).** The processor has its own temperature sensor. The manufacturer gives no conversion to degrees, so the page shows the raw reading only; it is useful to see changes, not absolute values.

## Advanced (collapsed block)

Rarely needed settings. Nothing in this block changes factory data.

* **Radio power**: +10 dBm (longest range, more current) down to -19 dBm (only at arm's length). Default +3 dBm. Stored in the tag.
* **Watchdog**: restarts the tag if the firmware hangs for more than 15 s. Default on; switch it off only when testing. Stored in the tag.
* **Reboot tag**: restarts the tag (the boot signal shows it). OpenDisplay clients can reboot it as well.
* **Power**: deep sleep for n seconds, auto-sleep window, status line.
* **OpenDisplay commands**: version, configuration and manufacturer data as an OpenDisplay client sees them; stream orientation and slot.

## For developers (collapsed block)

Test and discovery commands used while the firmware was developed: LED colours by hand (about 20 s), panel test steps, NFC chip scan / read / pin watch, a free hex command field, and the log.
**Buttons marked with a warning sign (⚠) are dangerous**: they write to the persistent memory of the tag's NFC chip. A wrong value can leave NFC unusable. The page asks for confirmation each time.
Use them only if you know what you are doing. The NFC chip is not used by the firmware yet.

## If something does not work

* Not in the device list: tick "show all devices"; make sure no other phone or computer is connected; wait one "poll" interval.
* Upload stops: choose "with confirmation"; come closer (the tag's radio power setting); check that the battery voltage is above 2.7 V.
* Three red flashes after a refresh: the panel did not answer or the upload failed; see the log (block "For developers"), try again, then reboot the tag.
* Ghost images: use the clean-up (or enable it in the slideshow).
* Nothing works after power-up: no LED sequence at all means the firmware did not start; see [`../firmware/FLASHING.md`](../firmware/FLASHING.md).
