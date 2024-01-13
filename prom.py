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
    print("LOCATION environment variable not set. Create .env with the LOCATION env var in it set to your local airport code.")
    sys.exit(1)

phidgets_serial = os.environ.get("PHIDGETS_SERIAL")
if loc is not None:
    print("PHIDGETS_SERIAL:", loc)
else:
    print("PHIDGETS_SERIAL environment variable not set. Create .env with the PHIDGETS_SERIAL env var in it set to your local airport code.")
    sys.exit(1)

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

labels = [loc]

TEMPERATURE_GAUGE = Gauge(
    'temperature_gauge',
    'Temperature Celsius',
    ['symbol', 'location']
)

HUMIDITY_GAUGE = Gauge(
    'humidity_gauge',
    'Humidity Percent',
    ['symbol', 'location']
)


TEMPERATURE_CHANGE_COUNT = Counter(
    'temperature_change_count',
    'Temperature Change Count',
    ['symbol', 'location']
)

HUMIDITY_CHANGE_COUNT = Counter(
    'humidity_change_count',
    'Humidity Change Count',
    ['symbol', 'location']
)

TEMPERATURE_HIST = Histogram(
    'temperature_celsius',
    'Temperature Celsius',
    ['symbol', 'location']
)

HUMIDITY_HIST = Histogram(
    'humidity_percent',
    'Humidity Percent',
    ['sybmol', 'location'] #labels
)

@app.route('/')
def index():
    start_time = time.time()
    REQUEST_COUNT.labels('GET', '/', 200).inc()
    response = jsonify(message='Query /metrics for... metrics!')
    REQUEST_LATENCY.labels('GET', '/').observe(time.time() - start_time)
    return response

def onTempChange(self, sensorValue, sensorUnit):
    # print("SensorValue: " + str(sensorValue) " " + str(sensorUnit.symbol))
    TEMPERATURE_CHANGE_COUNT.labels(sensorUnit.symbol, loc).inc()
    TEMPERATURE_HIST.labels(sensorUnit.symbol, loc).observe(sensorValue)
    ## TEMPERATURE_GAUGE.inc()      # Increment by 1
    ## TEMPERATURE_GAUGE.dec(10)    # Decrement by given value
    TEMPERATURE_GAUGE.labels(sensorUnit.symbol, loc).set(sensorValue)   # Set to a given value


def onHumidityChange(self, sensorValue, sensorUnit):
    # print("SensorValue: " + str(sensorValue) + " " + str(sensorUnit.symbol, loc))
    HUMIDITY_CHANGE_COUNT.labels(sensorUnit.symbol, loc).inc()
    HUMIDITY_HIST.labels(sensorUnit.symbol, loc).observe(sensorValue)
    HUMIDITY_GAUGE.labels(sensorUnit.symbol, loc).set(sensorValue)   # Set to a given value

if __name__ == '__main__':    
    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput1 = VoltageRatioInput()

    voltageRatioInput0.setIsHubPortDevice(True)
    voltageRatioInput0.setHubPort(0)
    voltageRatioInput0.setDeviceSerialNumber(phidgets_serial)

    voltageRatioInput1.setIsHubPortDevice(True)
    voltageRatioInput1.setHubPort(1)
    voltageRatioInput1.setDeviceSerialNumber(622942)

    voltageRatioInput0.setOnSensorChangeHandler(onTempChange)
    voltageRatioInput1.setOnSensorChangeHandler(onHumidityChange)

    voltageRatioInput0.openWaitForAttachment(5000)
    voltageRatioInput1.openWaitForAttachment(5000)

    # Sensor Types: SENSOR_TYPE_1125_HUMIDITY, SENSOR_TYPE_1125_TEMPERATURE
    voltageRatioInput0.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1125_TEMPERATURE)
    voltageRatioInput1.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1125_HUMIDITY)

    app.run(host='0.0.0.0', port=5000)

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    voltageRatioInput0.close()
    voltageRatioInput1.close()
