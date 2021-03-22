# Firmware for hall-sensor based filament diameter sensors.
# Reads analog value from the sensor and provides a mapped and filtered diameter
# reading over I2C or UART
# Runs on Raspberry Pi Pico ($4)
# Licensed MIT by John Moser
#
# Threads and power usage:
#  - Main loop:  block on i2c
#  - LED:  sleep_ms() or block on q.get()
#  - sensor:  sleep_us(1); might be able to reduce this to event-driven
#
# Communications have the following aspects:
#  - Numbers are unsigned fixed-point 24-bit, using 10 bits for the
#    fraction.  This gives 1/1024, which can be rounded to represent three
#    decimal places.  The range is 0 to 16383.(1023/1024)
#  - Communications over UART are Reed-Solomon coded.
#
# Note the ADC is noisy and has a resolution of about 7.85 bits[1] in the
# initial RPi Pico release.  All readings from the ADC are MSB-aligned:
# padding to 14 bits is added as the least-significant bits of the reading.
# There is no practical difference between 14/10 fixed-point and a 24-bit
# integer for the calculations here, so a special case is not made.
#
# [1] https://pico-adc.markomo.me/

from machine import Pin, ADC, I2C
from utime import sleep_ms, sleep_us
from os import size
from numpy.polynomial.polynomial import Polynomial
from numpy import mean
from queue import Queue
from threading import Thread
from unireedsolomon import RSCoder
import init

# LED states
LED_START = 1
LED_THINKING = 2
LED_COMPLETE = 3
LED_FAULT = 4

def init(config, led):
    dia_sensor = []
    # FIXME:  Should there be only one response Queue?
    for x in config.keys():
        # Initialize only if enabled
        if config[x].get('enabled', 0) == 1:
            dia_sensor[x] = {'queue': Queue(), 'reading': Queue()}
            (dia_sensor[x]['sensor'], dia_sensor[x]['curve'], d) =
                diameter_sensor.init_one(config[x], led_queue)
            t_sensor = Thread(target = sensor_task,
                              args = (dia_sensor[x]['sensor'],
                                      dia_sensor[x]['queue'],
                                      dia_sensor[x]['reading']))
            config[x].update(d)
    return (dia_sensor, config)

def init_one(config, led):
    u"""Initialize the board to a known state."""
    try:
        adc = config['adc']
    except:
        # ADC 0 on GP27, adjacent to AGND
        adc = 27
        config['adc'] = adc
    hall_sensor = machine.ADC(adc)

    # Generate calibration curve
    calibration_table = config.get('calibration',[])
    try:
        curve = get_calibration_polynomial(calibration_table)
    except:
        curve = None

    return (hall_sensor, curve, config)

def sensor_task(hall_sensor, q, qo):
    ma_length = 50 # Number of elements in moving average
    readings = []
    # XXX:  Does a 50µs delay matter?
    while True:
        # If there's anything in q, send a reading to qo
        q.get()
        readings.clear()
        # 12-bit ADC readings are left-aligned to 24 bits, then
        # reduced to 8-bit resolution.
        for x in range(ma_length):
            readings.append((hall_sensor.read_u16() << 12) & 0xf00)
            #sleep_us(1)
        qo.put(mean(readings))

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
def get_diameter(reading, curve):
    u"""Retrieve the diameter reading from the Hall Sensor."""
    # Subtract the reading from the polynomial, then find the roots.
    # The smallest root is the diameter.
    curve.coef[2] -= reading
    return min(curve.roots())

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

def calibrate(sensor, sample_diameter):
    u"""Adds a sample diameter to the calibration table."""
    # Unnecessary?  Migrate into a bigger function?
    return {'reading': sensor.read_u16(), 'diameter': sample_diameter}

def get_calibration_polynomial(calibration_table):
    u"""From calibration points, computes a best-fit quadratic equation."""
    return Polynomial.fit(
        [x['reading'] for x in calibration_table],
        [y['diameter'] for y in calibration_table],
        2)
    #
    # Because the Hall Effect sensor reading decreases with greater distance,
    # the smaller value of regression.roots() is the maximum distance sensed,
    # and all values sought are X being less than this.
    #
    # However, if the sensor never reads 0, then it will be everything to the
    # left of the vertex.  This is likely the better approach; it's just
    # setting the upper bound for diameter.

if __name__ == "__main__":
  main()
