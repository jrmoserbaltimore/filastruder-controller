# Firmware for hall-sensor based filament diameter sensors.
# Reads analog value from the sensor and provides a mapped and filtered diameter
# reading over I2C (optional analog output)
# Runs on Raspberry Pi Pico ($4)
# Licensed CC-0 / Public Domain by John Moser

from machine import Pin, ADC, I2C
from utime import sleep
from os import size
from numpy import Polynomial

def main():
    # Onboard LED, for feedback
    led = machine.Pin(25, machine.Pin.OUT)
    # ADC 0 on GP26
    hall_sensor = machine.ADC(26)
    # I2C0 using pins 0 and 1.  Address is 43
    i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

    init(led)

def init(led):
    u"""Initialize the board to a known state."""
    # Definitely set the state to on, then off
    led.on()
    utime.sleep_ms(1000)
    led.off();
    # Blink four times; watches tick 6 per second
    for i in range(8)
        ledtoggle()
        utime.sleep_ms(125)
    # Make sure it's off
    led.off();
    
def signal_fault(OnboardLED):
    u"""Blinks the LED steadily to indicate a fault.
    Call as a thread; destroy to end fault."""
    # Blink once per second
    while True:
        OnboardLED.toggle()
        utime.sleep_ms(500)

def get_diameter(sensor, curve):
    u"""Retrieve the diameter reading from the Hall Sensor."""
    reading = sensor.read_u16()

###############
# Calibration #
###############

# Calibration works as follows:
#
#   - A json file contains { 'calibrate': [ {'reading': HALL_READING, 'diameter': IN_MM}, ... ]}
#   - Calibration is read in from this file
#   - A certain M-code on the host (M407 D<width>) triggers a sample reading, which
#     adds the Hall reading and the diameter to the 'calibrate' key
#   - A certain M-code (M407 D<width> S<reading>) provides a diameter and reading
#   - Upon loading or updating the calibration info, a quadratic polynomial is fit to the
#     data
#
# The strength of a magnetic field is inversely proportional to the square of the
# distance between the sensor and the magnet:
#
#   f(d) = ad**2 + bx + c
#
# Smaller d values (i.e. x values) lead to larger f(d) values; thus the values of d
# greater than zero, left of the vertex, and with f(d) >= 0 is the domain.
#
# The calibration output is the polynomial, and it is solved for x (diameter) given a
# value of y (Hall Sensor reading).

def calibrate(sensor, sample_diameter):
    u"""Adds a sample diameter to the calibration table."""
    # Unnecessary?  Migrate into a bigger function?
    return {'reading': sensor.read_u16(), 'diameter': sample_diameter}

def get_calibration_polynomial(calibration_table):
    u"""From calibration points, computes a best-fit quadratic equation."""
    pass;
    # TODO:
    #  regression = Polynomial.fit(X points, Y points)
    #
    # Because the Hall Effect sensor reading decreases with greater distance,
    # the smaller value of regression.roots() is the maximum distance sensed,
    # and all values sought are X being less than this.
    #
    # However, if the sensor never reads 0, then it will be everything to the
    # left of the vertex.  This is likely the better approach; it's just
    # setting the upper bound for diameter.

def load_calibration_table(path)
    u"""Open a calibration table from a file."""
    try:
        # Don't load if the file is like, way big d00d
        if (os.size(path) > 5120) raise ImportError
        with open(path, 'r') as f:
            table = ujson.load(f)
    except:
    table = {}
    return Table
 
if __name__ == "__main__":
  main()
  