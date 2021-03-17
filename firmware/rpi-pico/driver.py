# Firmware for hall-sensor based filament diameter sensors.
# Reads analog value from the sensor and provides a mapped and filtered diameter
# reading over I2C (optional analog output)
# Runs on Raspberry Pi Pico ($4)
# Licensed CC-0 / Public Domain by John Moser
#
# Threads and power usage:
#  - Main loop:  block on i2c
#  - LED:  sleep_ms() or block on q.get()
#  - sensor:  sleep_us(1); might be able to reduce this to event-driven

from machine import Pin, ADC, I2C
from utime import sleep_ms, sleep_us
from os import size
from numpy.polynomial.polynomial import Polynomial
from numpy import mean
from queue import Queue
from threading import Thread
#import _thread

# LED states
LED_START = 1
LED_THINKING = 2
LED_COMPLETE = 3
LED_FAULT = 4

def main():
    sensor_queue = Queue()
    reading_queue = Queue()
    reading_response = Queue()
    
    (i2c,led,led_queue,hall_sensor,calibration_table,curve) = init()
    
    t_sensor = Thread(target = sensor_task,
                      args = (hall_sensor, reading_queue, reading_response))
    while True:
        pass
        # TODO:
        #   - block and wait for i2c command (i2c.recv(???))
        #   - when i2c requests diameter:
        # reading_queue.put(1)
        # i2c.send(get_diameter(reading_response.get(), curve))
        #
        #   - when i2c signals calibrate <diameter>,
        #     take a reading into the calibration table

        

def init():
    u"""Initialize the board to a known state."""
    calibration_path = "/diameter-calibration-table.json"
    # Onboard LED, for feedback
    led = machine.Pin(25, machine.Pin.OUT)
    led_queue = Queue()

    t_led = Thread(target = led_task, args = (led, led_queue))

    # Signal bootup
    led_queue.put(LED_START)
    led_queue.put(LED_THINKING)
    
    # I2C0 using pins 0 and 1.  Address is 43
    # FIXME:  Make address configurable
    i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
    i2c.init(I2C.SLAVE, addr=43)
    
    # ADC 0 on GP27, adjacent to AGND
    hall_sensor = machine.ADC(27)
    # Load calibration table
    calibration_table = load_calibration_table(calibration_path)
    curve = get_calibration_polynomial(calibration_table)
    
    led_queue.put(LED_COMPLETE)
    # send all the initialized stuff back
    return (i2c, led, led_queue, hall_sensor, calibration_table, curve)

def led_task(led, q):
    u"""a"""
    counter = 0
    while True:
        # Certain actions loop until interrupted
        if c in [LED_THINKING, LED_COMPLETE, LED_FAULT]:
            if !q.empty(): c = q.get()
        else:
            c = q.get()

        if c == LED_START:
            # Definitely set the state to on, then off
            led.on()
            utime.sleep_ms(1000)
            led.off()
        elif c == LED_THINKING:
            led.toggle()
            utime.sleep_ms(500)
        elif c == LED_COMPLETE:
            # Toggle every 1/8 seconds for 1 second
            counter = counter == 0 ? 8 : counter - 1
            led.toggle()
            utime.sleep_ms(125)
            if counter == 0:
                led.off()
                c = 0 # Clear c
        elif c == LED_FAULT:
            led.toggle()
            utime.sleep_ms(1000)

def sensor_task(hall_sensor, q, qo):
    ma_length = 50 # Number of elements in moving average
    readings = []
    # Repeatedly take readings for a simple moving average
    # XXX:  Does a 50µs delay matter?  If not, block on q.get(),
    # and then set a counter and loop to get the 50 readings.
    # This reduces power usage.
    while True:
        readings.append(hall_sensor.read_u16())
        if readings.len() > ma_length: readings.pop(0)
        sleep_us(1)
        # If there's anything in q, send a reading to qo
        try:
            q.get(block=False)
            qo.put(mean(readings))
        except:
            pass

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
        [x['reading'] for x in calibration_table['calibration']],
        [y['diameter'] for y in calibration_table['calibration']],
        2)
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
