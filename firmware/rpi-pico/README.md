# Pi Pico firmware

The firmware here controls both the Filastruder and the Filawinder.

# Combined controller

This controller runs the Filawinder and Filastruder.

## BOM

* 1 Pi Pico ($4)
<!--* 1 DRV8833 2-channel motor controller board ($0.56 ea)-->
* 2 L9110S DC motor drivers ($0.09 ea)
* 1 Rotary Encoder module with switch ($0.90 ea)
* 2 ADS1115 I2C module ($1.73)
* 1 1.8 inch ST7735 TFT module ($3.39)
  * Alternative: 1602 16x2 character display ($1.75)
  * Alternative: 2.4 inch 240x320 ILI9341 TFT module ($6.78)

Total: $10.10 ($13.41 with 2.4 inch display)

This replaces:

* Arduino Nano ($20)
* Stall controller ($10)
* Custom board (?)
* Front panel buttons and switches (except power)


## Overview

Because the Pico can take instructions over UART, one can control the
other, or a Pi Zero can control both.  This allows for placing controls
only on the Filawinder, or controlling via a Pi Zero instead of a front
panel.  When split, more UARTs and I2C ports are available to
communicate between the two microcontrollers.

Likewise, the four-channel ADS1115 I2C module ($1.73), used for the
laser position sensor, can also send temperature readings from the
Filastruder to the Filawinder.  This allows full control from the
Filawinder, saving on the screen, Pico, and rotary coder, about $10:

```
      Filastruder      Filawinder
                         Pi Pico
  [Heater]←----------[PWM0]
                     [GP2,3]←----------------[Rotary Coder]
              [ADS0]→[I2C0]    [ADC2]←-------[Diameter Sensor]
   [Motor]←---[DRV]←-[PWM3]    [I2C1]←[ADS1]←-[Laser Sensor]
  [Cooling fan]←-----[PWM4]    [GP22]←-------[Rotary Coder Button]
  [Display]←---------[SPI1]    [PWM2]-------→[Wind Motor]
  (Display on Filawinder)      [PWM1]-------→[Servo]
   [Extruder RPM]←---[GP14]    [UART0]←------[Comm/Pi Zero]

ADS0:
  Thermistor
  ACS712 Current Sensor
```

*XXX: Connect Comm to a watchdog circuit to cut power to the heater
and motor during fault, and have Pi Zero perform this function instead
if present?*

## Filament Width Closed-Loop

There are several sensors in the Filastruder and Filawinder:

* Filastruder
  * Temperature
  * Motor current
  * Motor RPM (A3141 hall sensor and several magnets)
* Filawinder
  * Filament diameter
  * Filament loop height

The Filawinder controller uses a diameter sensor to tune operation.
It primarily reduces speed to increase tension on the filament and
reduce diameter, or increases speed to reduce tension and increase
diameter.

In the Filastruder, the temperature is measured by thermocouple; a
current sensor tracks motor current; and a hall switch tracks motor RPM
by equally-spaced magnets, 8 of which corresponds to 2.5 seconds at
3 RPM.  The Filastruder also uses a current sensor on the motor,
restricting to below 1.5A.

The Filawinder's wind motor can be measured by RPM, but the diameter
of the spool increases as more filament is spooled.  Linear velocity
increases with constant angular velocity (CAV).  To approximate
constant linear velocity (CLV), the Filawinder uses the laser sensor to
maintain the height of the filament loop.

The Filawinder controller here additionally measures filament diameter.
It increases winding speed when the diameter is too narrow, and
decreases when too wide, to the limits of the filament loop height.

When connected with the Filastruder, the controller also adjusts
temperature.  Together, the strategy is as follows:

* Aim for target temperature
* When diameter is too narrow:
  * Reduce temperature toward target;
  * Increase cooling toward maximum;
  * Increase winding speed toward maximum filament loop height;
  * Reduce temperature toward minimum
* When diameter is too thick:
  * Raise temperature toward target;
  * Decrease cooling toward minimum;
  * Decrease winding speed toward minimum filament loop height;
  * Raise temperature toward maximum

## Main Panel

I2C on `GP0` and `GP1` control the display.

Several buttons are provided:

* `GP10` and `GP11`:  Up and down (rotary encoder)
* `GP12`:  Select (push-button on rotary encoder)

The display allows menu selection for heater and motor control,
extrusion profile, serial port control, and other configuration.  It
also displays statistics.

### Serial LCD

Preferred display is a 128x160 ST7735 module at 1.8 inch.  These cost
some $3.50.

Alternately, a $6 2.4 inch 240x320 ILI9341 module works as well.

## PID Controller

The PID controller uses `ADC 2` and `ADC_VREF` on `GP28` and pin 35 to
measure the thermistor on the barrel, and `PWM 3` on `GP6` and `GP7` to
drive the heater via a MOSFET.

This PID controller has an adaptive tuning mode, using data collected
during operation rather than during a tuning cycle.

## Motor Controller

The motor controller uses `PWM 4` on `GP8` and `GP9` to drive a MOSFET
driving the motor.  It sets motor speed via configuration.

## Serial Controller

`UART 0` on `GP16` and `GP17` provides bidirectional communication
between the Filastruder and Filawinder, or between both and a Pi Zero.
This allows remote and automated control of the Filastruder.

Serial communications use Reed-Solomon coding with a high degree of
redundancy to deal with an unreliable link.

### Closed-Loop Control

When the Filastruder and Filawinder both supply data, the Pi Pico or a
Pi Zero can analyze this and instruct one or both to make adjustments.
The Filawinder handles this if a Zero is not used, as it requires a
filament diameter sensor, which requires the filament to be drawn
mechanically at a controlled rate.

### Photosensor

The laser and sensor board are required, although the sensor is four
analog outputs using resistors.  Tying each of these to a resistor and
capacitor creates a digital signal, but not necessarily effective.

Instead, a cheap I2C ADS module is used.  This provides signal for as
much as 1-2 meters of cable length.

### Control mapping

The display allows menu selection for motor control, filament guide
setup, target diameter, serial port control, and other configuration.
It also displays statistics.

The controls change in this layout.  A software menu provides maunal
or auto mode, as well as servo position and range setup.  The rotary
encoder controls this.

* Manual/Auto switch:  Software menu
* Servo position and range:  Software menu
  * Setup walks through first adjusting servo position, press button,
    adjust to end position, press button

