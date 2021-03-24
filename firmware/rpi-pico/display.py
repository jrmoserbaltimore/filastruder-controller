# Filastruder/Filawinder firmware
# Runs on Raspberry Pi Pico ($4)
# Licensed MIT by John Moser
#
# Display controller

from importlib import import_module

class Display:
    u"""The display device, for outputting menus."""

    def __init__(port, driver, width, height):
        # Loads the module for the specific driver
        # FIXME:  Do some sane exception handling here
        try:
            self._display = import_module('rgb_display.' + driver)
        except:
            return None
         # TODO:  Create display here
         # XXX:  How do we handle displays with extra pins?

    # TODO:  Menu drawing functions