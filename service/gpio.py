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
        # request all sensors' configuration so to filter sensors of interest
        self.add_configuration_listener("sensors/#", 1)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
    
    # What to do when shutting down
    def on_stop(self):
        pass
        
    # receive a callback and send a message to the hub
    def event_callback(self, pin):
        if pin not in self.pins: return
        sensor_id = self.pins[pin]
        value = 1 if GPIO.input(pin) else 0
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
            # if the raw data is cached, take it from there, otherwise request the data and cache it
            cache_key = "/".join([str(pin)])
            if self.cache.find(cache_key): 
                data = self.cache.get(cache_key)
            else:
                GPIO.setup(pin, GPIO.IN)
                data = GPIO.input(pin)
                self.cache.add(cache_key, data)
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
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, data)
    
    # setup pull up/down resistor
    def get_pull_up_down(self, configuration):
        pass


    # What to do when receiving a new/updated configuration for this module    
    def on_configuration(self,message):
        # sensors to register
        if message.args.startswith("sensors/"):
            sensor_id = message.args.replace("sensors/","")
            sensor = message.get_data()
            # a sensor has been deleted
            if message.is_null:
                for pin in self.pins:
                    id = self.pins[pin]
                    if id != sensor_id: continue
                    GPIO.remove_event_detect(pin)
                    del self.pins[pin]
            # a sensor has been added/updated
            else: 
                # filter in only relevant sensors
                if "service" not in sensor or sensor["service"]["name"] != self.name or sensor["service"]["mode"] != "passive": return
                if "edge_detect" not in sensor["service"]["configuration"]: return
                # configuration settings
                configuration = sensor["service"]["configuration"]
                if not self.is_valid_configuration(["pin", "edge_detect"], configuration): return
                pin = configuration["pin"]
                edge_detect = configuration["edge_detect"]
                # register the pin
                if pin in self.pins and sensor_id != self.pins[pin]:
                    self.log_error("pin "+str(pin)+" already registered with sensor "+self.pins[pin])
                    return
                if pin in self.pins:
                    GPIO.remove_event_detect(pin)
                self.pins[pin] = sensor_id
                # set pull up / down resistor
                pull_up_down = self.get_pull_up_down(configuration)
                if pull_up_down is not None: GPIO.setup(pin, GPIO.IN, pull_up_down=pull_up_down)
                else: GPIO.setup(pin, GPIO.IN)
                # add callbacks
                if edge_detect == "rising": GPIO.add_event_detect(pin, GPIO.RISING, callback=self.event_callback)
                elif edge_detect == "falling": GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.event_callback)
                elif edge_detect == "both": GPIO.add_event_detect(pin, GPIO.BOTH, callback=self.event_callback)
                else:
                    self.log_error("invalid edge_detect: "+edge_detect)
                    return
                self.log_debug("registered sensor "+sensor_id)