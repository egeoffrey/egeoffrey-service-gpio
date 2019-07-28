### service/gpio_orangepi: read/write from an orangepi GPIO
## HOW IT WORKS: 
## DEPENDENCIES:
# OS: 
# Python: OPI.GPIO
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
#   optional: edge_detect (rising|falling|both)

import OPi.GPIO

from gpio import Gpio

class Gpio_orangepi(Gpio):
    gpio_object = OPi.GPIO
    # setup pull up/down resistor
    def get_pull_up_down(self, configuration):
        pass
