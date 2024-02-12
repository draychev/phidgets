#!/usr/bin/env python3

import os
import sys
import time
import subprocess
import re
import threading

from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *

loc = os.environ.get("LOCATION")
if loc is not None:
    print("LOCATION:", loc)
else:
    print("LOCATION env var is not set. Create .env and add 'export LOCATION=xyz'")
    sys.exit(1)

phidgets_serial = os.environ.get("PHIDGETS_SERIAL")
if phidgets_serial is not None:
    print("PHIDGETS_SERIAL:", phidgets_serial)
else:
    print("PHIDGETS_SERIAL env var is not set. Create .env and add 'export PHIDGETS_SERIAL=123'")
    sys.exit(1)

system_info = os.uname()
computer_name = system_info.nodename

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

labels = [loc]

TEM_GAUGE = Gauge('temperature_gauge', 'Temperature', ['symbol', 'location'])
TEM_HIST = Histogram('temperature_histogram', 'Temperature', ['symbol', 'location'])

HUM_GAUGE = Gauge('humidity_gauge', 'Humidity', ['symbol', 'location'])
HUM_HIST = Histogram('humidity_histogram', 'Humidity', ['sybmol', 'location'])

PING_GAUGE = Gauge('ping_gauge', 'Ping', ['name', 'location'])
PING_HIST = Histogram('ping_histogram', 'Ping', ['name', 'location'])

@app.route('/')
def index():
    return redirect('/metrics')

def onTempChange(self, sensorValue, sensorUnit):
    temperature = sensorValue
    symbol = sensorUnit.symbol

    # sensorUnit.symbol for temperature sensor is "°C"
    # we are converting the temperature - so we rewrite symbol to "°F"
    temperature = (temperature * 9/5) + 32
    symbol = "°F"

    TEM_HIST.labels(symbol, loc).observe(temperature)
    TEM_GAUGE.labels(symbol, loc).set(temperature)

def ping_and_get_time():
    # Execute the ping command
    command = ['ping', '-c', '1', '8.8.8.8']
    try:
        output = subprocess.check_output(command, universal_newlines=True)

        # Use regex to find the time value in the output
        match = re.search(r'time=(\d+\.\d+) ms', output)
        if match:
            # Return the time in milliseconds
            return float(match.group(1))
        else:
            return "Time not found in ping output."
    except subprocess.CalledProcessError as e:
        return f"Failed to execute ping: {str(e)}"

def ping_every_5_seconds():
    while True:
        ping_time = ping_and_get_time()
        PING_HIST.labels(computer_name, loc).observe(ping_time)
        PING_GAUGE.labels(computer_name, loc).set(ping_time)
        print(time_result)
        time.sleep(5)

def onHumidityChange(self, sensorValue, sensorUnit):
    HUM_HIST.labels(sensorUnit.symbol, loc).observe(sensorValue)
    HUM_GAUGE.labels(sensorUnit.symbol, loc).set(sensorValue)

if __name__ == '__main__':
    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput1 = VoltageRatioInput()

    voltageRatioInput0.setIsHubPortDevice(True)
    voltageRatioInput0.setHubPort(0)
    voltageRatioInput0.setDeviceSerialNumber(int(phidgets_serial))

    voltageRatioInput1.setIsHubPortDevice(True)
    voltageRatioInput1.setHubPort(1)
    voltageRatioInput1.setDeviceSerialNumber(int(phidgets_serial))

    voltageRatioInput0.setOnSensorChangeHandler(onTempChange)
    voltageRatioInput1.setOnSensorChangeHandler(onHumidityChange)

    voltageRatioInput0.openWaitForAttachment(5000)
    voltageRatioInput1.openWaitForAttachment(5000)

    # Sensor Types: SENSOR_TYPE_1125_HUMIDITY, SENSOR_TYPE_1125_TEMPERATURE
    voltageRatioInput0.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1125_TEMPERATURE)
    voltageRatioInput1.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1125_HUMIDITY)


    # Create a thread that runs the ping_every_5_seconds() function
    thread = threading.Thread(target=ping_every_5_seconds)
    # Daemon threads automatically shut down when the main program exits
    thread.daemon = True
    thread.start()

    app.run(host='0.0.0.0', port=5000)

    voltageRatioInput0.close()
    voltageRatioInput1.close()
