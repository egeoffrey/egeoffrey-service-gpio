# gpio common functions

import datetime
import json
import time
import json

from sdk.python.module.service import Service
from sdk.python.module.helpers.message import Message

import sdk.python.utils.exceptions as exception

class Gpio(Service):
    # What to do when initializing
    def on_init(self):
        # map pin with sensor_id
        self.pins = {}
        
    # What to do when running
    def on_start(self):
        self.gpio_object.setwarnings(False)
        self.gpio_object.setmode(self.gpio_object.BCM)
    
    # What to do when shutting down
    def on_stop(self):
        pass
        
    # receive a callback and send a message to the hub
    def event_callback(self, pin):
        if pin not in self.pins: return
        sensor_id = self.pins[pin]
        value = 1 if self.gpio_object.input(pin) else 0
        self.log_debug("GPIO input on pin "+str(pin)+" is now "+str(value))
        message = Message(self)
        message.recipient = "controller/hub"
        message.command = "IN"
        message.args = sensor_id
        message.set("value", value)
        self.send(message)

    # What to do when receiving a request for this module
    def on_message(self, message):
        sensor_id = message.args
        # ensure configuration is valid
        if not self.is_valid_configuration(["pin"], message.get_data()): return
        pin = message.get("pin")
        if message.command == "IN":
            self.gpio_object.setup(pin, self.gpio_object.IN)
            data = self.gpio_object.input(pin)
            # send the response back
            message.reply()
            message.set("value", data)
            self.send(message)
        elif message.command == "OUT":
            data = int(message.get("value"))
            if data != 0 and data != 1: 
                self.log_error("invalid value: "+str(data))
                return
            self.log_info("setting GPIO pin "+str(pin)+" to "+str(data))
            self.gpio_object.setup(pin, self.gpio_object.OUT)
            self.gpio_object.output(pin, data)
    
    # setup pull up/down resistor
    def get_pull_up_down(self, configuration):
        pass

    # What to do when receiving a new/updated configuration for this module    
    def on_configuration(self,message):
        # register/unregister the sensor
        if message.args.startswith("sensors/"):
            if message.is_null: 
                sensor_id = self.unregister_sensor(message)
                if sensor_id is not None:
                    # remove any previously configured edge detection
                    for pin in self.pins:
                        id = self.pins[pin]
                        if id != sensor_id: continue
                        self.gpio_object.remove_event_detect(pin)
                        del self.pins[pin]
            else: 
                sensor_id = self.register_sensor(message, ["pin"])
                if sensor_id is not None:
                    sensor = message.get_data()
                    # for passive sensors only we need to register the edge detection
                    if sensor["service"]["mode"] == "passive":
                        # configuration settings
                        configuration = sensor["service"]["configuration"]
                        if not self.is_valid_configuration(["edge_detect"], configuration): return
                        pin = configuration["pin"]
                        edge_detect = configuration["edge_detect"]
                        # register the pin
                        if pin in self.pins and sensor_id != self.pins[pin]:
                            self.log_error("pin "+str(pin)+" already registered with sensor "+self.pins[pin])
                            return
                        if pin in self.pins:
                            self.gpio_object.remove_event_detect(pin)
                        self.pins[pin] = sensor_id
                        # set pull up / down resistor
                        pull_up_down = self.get_pull_up_down(configuration)
                        if pull_up_down is not None: self.gpio_object.setup(pin, self.gpio_object.IN, pull_up_down=pull_up_down)
                        else: self.gpio_object.setup(pin, self.gpio_object.IN)
                        # add callbacks
                        if edge_detect == "rising": self.gpio_object.add_event_detect(pin, self.gpio_object.RISING, callback=self.event_callback)
                        elif edge_detect == "falling": self.gpio_object.add_event_detect(pin, self.gpio_object.FALLING, callback=self.event_callback)
                        elif edge_detect == "both": self.gpio_object.add_event_detect(pin, self.gpio_object.BOTH, callback=self.event_callback)
                        else:
                            self.log_error("invalid edge_detect: "+edge_detect)
                            return
