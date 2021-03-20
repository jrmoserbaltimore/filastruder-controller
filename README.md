# Filastruder/Filawinder controller

This is an alternate controller for the Filastruder and Filawinder setup.
It uses work based on [Tom Sanladerer's InFiDEL diameter sensor](https://www.prusaprinters.org/prints/57154-infiDANK),
a low-cost filament diameter sensor designed to allow FDM printers to correct for filament
diameter deviations while printing.  Doing this on both ends maximizes ultimate precision.

Using closed-loop feedback to maintain filament diameter during extrusion may produce
siginficant deviation, as the sensor is potentially over a meter away from the nozzle.
While commercial filament claims 1.70-1.80—achievable with a carefully tuned Filastruder—or
in some cases 1.73-1.77, a less-tuned setup may have more deviation.  With a sensor on
the printer, a range of 1.50-1.80 can work appreciably well, easily maintained by the
Filastruder.

At the same time, allowing the lower bound to fall more is not ideal, especially with
longer Bowden tubes.  Remaining closer to the upper bound for smooth operation improves
retraction characteristics, and the controller attempts to keep tolerances as narrow as
achievable, suitable for printers without a filament diameter sensor.

This replaces the Filastruder's $35 PWM with a $4 Pi Pico, $1.50 of switches, and a $2
display.  For the Filawinder, a $20 Arduino Nano and custom controller board are replaced
with a $4 Pi Pico and a $2 MOSFET control board.  Together, this can add up to about $40
cost reduction.

# Design basics

This uses the the [Raspberry Pi Pico](https://www.raspberrypi.org/products/raspberry-pi-pico/)
microcontroller board for its low-cost ADC, used to read thermistors and Hall sensors.
It uses PWM to control heaters and motor speed via a MOSFET.

If appreciably close, UART over 1-2 meters of cable can be used for communication between
the Filastruder and Filawinder.  This requires little throughput, and the firmware uses
Reed-Solomon coding with a high degree of redundancy to deal with an unreliable link.
Communication between the Filastruder and Filawinder allows for temperature reduction
when increasing the spool rate raises the filament above the height sensor, and
temperatue increase when lowering the filament causes it to fall below the sensor.

Data on temperature, winding speed, height, and diameter can provide insight into the
properties of the material, for example to detect how efficiently a mixture of PET and
ethylene glycol is reacting to produce PETG.  Advanced controllers can use this to slow
the extrusion screw, increase temperature, and adjust the winding speed to increase
reaction rate, or otherwise adjust parameters.

## Display

*Cost:  $2*

A GM009605 operating over I2C provides read-out for filament diameter, winding speed,
temperature, motor speed, and other statistics, controlled by either the Pico or a Zero.

## Inputs

*Cost: $1.50*

The Filawinder uses three momentary switches for up, down, and select.
The menu allows selection of a winder, with the following options:

* Winder (1, 2, 3)
  * Enable (Yes, No, Auto)
  * Diameter target (up, down)
  * Diameter maximum (up, down)
  * Manual RPM target (up, down)
  * Calibrate winder guide
  * Calibrate diameter sensor
    * Select calibration (delete, update)
    * Create calibration (set diameter)
* Communications
  * Filastruder (UART0/1, disabled)
  * Control (UART0/1, disabled) (Zero)

The Filastruder menu controls the temperature and drive speed:

* Profile (select, create)
  * Temperature (up, down)
  * Drive speed (up, down)
* Communications
  * Filawinder (UART0/1, disabled)
  * Control (UART0/1, disabled)

## Optional components

### Pi Zero W Remote Control/UI/Comm

*Cost:  $10-$20*

A Pi Zero W can communicate with either microcontroller and make statistics available over
Wifi or Bluetooth, or act as a controller interface.  When connected by UART, either
Pico can relay data and commands to and from the Zero W; it's also possible to use two to
relay data over Bluetooth or Wifi, but this adds significant cost.

Daisy chaining is possible:  a number of Filawinders set up to spool from several
Filastruders can relay from each to the next, causing increasing link and CPU load the
longer the chain gets.  A number of Filawinders set up closer to the Zero W can shorten
the relay chain, for example having a Zero W between two Filawinders, each connected to a
Filastruder opposite the Zero.  This reduces the per-unit cost when extruding larger
amounts of filament, although this is an infrequent use case.

### Multi-Winder Control

A single Pico may receive three analog signals, operate two SPIs, run three PWMs, and
still have room for two UARTs and one one I2C or one UART and two I2Cs, plus two GPIOs.

Three PWMs can operate three motors, using input from three analog filament diameter
sensors.  Using a single block, 3-filament sensor, only one Pico is needed; the distance
to the motor PWMs should be considered.

# Parts

For the Pi Pico, use a low-cost header from AliExpress.  Signal voltage is 3.3V.
Plug a +1.8 to +5V.V source directly into `VBUS`, and a ground into `GND`.

I2C `SDA`/`SCL` are `GP0` and `GP1`, respectively.

The Hall sensor's signal goes to `GP27`, `ADC1`; its ground goes to pin 33, `AGND`,
directly adjacent.  Pin 36 is 3.3V and Pin 39 provides whatever power you're using;
select an appropriate Hall sensor.

### Calibration
The Pi Pico can handle calibration in several ways.  Each requires you to use a
number of calibration samples less than 1mm and round; a caliper is highly
recommended here.

Thonny can run Python directly on the board.  Plug the Pico into USB and use the
included program to give a continuous sensor readout.  Record the sensor values
for each diameter and enter them into `infidel.calibration.json` in the format:

```json
{
  'calibration':
  [
    {
     'reading': <sensor reading>,
     'diameter': <sample diameter>
    },
    ...
  ]
}
```

Multiple samples of a given diameter are allowed. `numpy` computes a quadratic
regression whenever calibration data is loaded (at power on) or added.

Alternatively, use a jumper wire to connect `GP15` and `GP14` (pins 20 and 19),
and the jump to pin 18 (GND) any of pin 17 (1.5mm), 16 (1.7mm), or 15 (2.0mm).
Use a drillbit of each precise diameter to give a sample.  When each pin is
jumped, it deletes all samples for that diameter; it then blinks each 1 second,
taking a sample for that diameter.

The last method is bidirectional communication over I2C, but this requires
host support.  The printer firmware may not support this.  Appropriate commands
add, delete, retrieve, or modify sample data.


## BOM

Costs total to $4.75 of electronics and bearings, plus 4 screws and a magent, about $5.

### Printed Parts
- 1 Block
- 1 Lever

Parts should preferably be printed in PETG, ABS, or ASA as PLA may creep significantly over time.

### Electronics
 - 1 Raspberry Pi Pico ($4)
 - 1 SS495A linear hall effect sensor (or comparable)

### Fasteners
- 4 M3x8 screws (eg ISO 4762 M3x8)
- 4 M3 nuts

### Other Hardware
- 1 6x2mm magnet (eg N35)
- 3 MR63 bearings (preferably ZZ)
- Short length of PTFE tube

### Calibration Accessories
Drill bits can be verified with calipers for shaft diameter and used as a
calibration tool.
