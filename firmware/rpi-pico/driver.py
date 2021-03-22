# Filastruder/Filawinder firmware
# Runs on Raspberry Pi Pico ($4)
# Licensed MIT by John Moser
#
# This is also the firmware for a diameter sensor to run on an FDM
# printer.
from machine import Pin, ADC, I2C
from utime import sleep_ms, sleep_us
from os import size
from numpy.polynomial.polynomial import Polynomial
from numpy import mean
from queue import Queue
from threading import Thread
from unireedsolomon import RSCoder

import diameter_sensor

def main():
    u"""Main program checks what function is configured"""
    config_path = "/filastruder-config.json"

    (config, i2c, led, led_queue) = init.init(config_path)

    # Diameter sensor setup
    if config.get('diameter sensor') == None:
        config['diameter sensor'] = []

    (dia_sensor, d) = diameter_sensor.init(config['diameter sensor'])
    config['diameter sensor'].update(d)

def init(config_path):
    u"""Initialize the board to a known state."""
    config = load_config(config_path)
    # Onboard LED, for feedback
    led = machine.Pin(25, machine.Pin.OUT)
    led_queue = Queue()

    t_led = Thread(target = led_task, args = (led, led_queue))
    # Signal bootup
    led_queue.put(LED_START)
    led_queue.put(LED_THINKING)

    i2cconfig = config['i2c']
    try:
        i2caddr = i2cconfig['address']
        i2csda = i2cconfig['sda']
        i2cscl = i2cconfig['scl']
    except:
        i2caddr = 43
        i2csda = 0
        i2cscl = 1
        i2cconfig['address'] = i2caddr
        i2cconfig['sda'] = i2csda
        i2cconfig['scl'] = i2cscl
        config['i2c'].update(i2caddr)
    i2c = machine.I2C(0, sda=machine.Pin(i2csda), scl=machine.Pin(i2csda), freq=400000)
    i2c.init(I2C.SLAVE, addr=i2caddr)

    led_queue.put(LED_COMPLETE)
    # send all the initialized stuff back
    return (config, i2c, led, led_queue)

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

def load_config(path)
    u"""Open a configuration file."""
    try:
        # Don't load if the file is like, way big d00d
        if (os.size(path) > 10240) raise ImportError
        with open(path, 'r') as f:
            table = ujson.load(f)
    except:
    config = {}
    return config

if __name__ == "__main__":
    main()
