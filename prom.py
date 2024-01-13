#!/usr/bin/env python3

import os
import sys
import time

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

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

labels = [loc]

TEM_GAUGE = Gauge('temperature_gauge', 'Temperature', ['symbol', 'location'])
HUM_GAUGE = Gauge('humidity_gauge', 'Humidity', ['symbol', 'location'])
TEM_HIST = Histogram('temperature_histogram', 'Temperature', ['symbol', 'location'])
HUM_HIST = Histogram('humidity_histogram', 'Humidity', ['sybmol', 'location'])

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

    app.run(host='0.0.0.0', port=5000)

    voltageRatioInput0.close()
    voltageRatioInput1.close()
