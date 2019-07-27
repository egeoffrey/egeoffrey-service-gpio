### service/gpio_raspi: read/write from a raspberry pi GPIO
## HOW IT WORKS: 
## DEPENDENCIES:
# OS: raspi-gpio, python-rpi.gpio
# Python: 
## CONFIGURATION:
# required: 
# optional: 
## COMMUNICATION:
# INBOUND: 
# - IN: 
#   required: pin
#   optional: 
# - OUT: 
#   required: pin, value
#   optional: 
# OUTBOUND:
# - controller/hub IN:
#   required: pin
#   optional: edge_detect (rising|falling|both) , pull_up_down (up|down)

import RPi.GPIO as GPIO

from gpio import Gpio

class Gpio_raspi(Gpio):
    
    # setup pull up/down resistor
    def get_pull_up_down(self, configuration):
        if "pull_up_down" in configuration:
            if configuration["pull_up_down"] == "up": return GPIO.PUD_UP
            elif configuration["pull_up_down"] == "down": return GPIO.PUD_DOWN
            else:
                self.log_error("invalid pull_up_down: "+configuration["pull_up_down"])
                return None
        else: return None
