#!/usr/bin/env python3

from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *

import time

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

TEMP_GAUGE = Gauge(
    'temp_gauge',
    'Temperature Celsius',
    ['symbol'] #labels
)

HUMIDITY_GAUGE = Gauge(
    'humidity_gauge',
    'Humidity Percent',
    ['symbol'] #labels
)


TEMP_CHANGE_COUNT = Counter(
    'temp_change_count',
    'Temperature Change Count',
    ['symbol'] #labels
)

HUMIDITY_CHANGE_COUNT = Counter(
    'humidity_change_count',
    'Humidity Change Count',
    ['symbol']
)

TEMP_HIST = Histogram(
    'temperature_celsius',
    'Temperature Celsius',
    ['symbol']
)

HUMIDITY_HIST = Histogram(
    'humidity_percent',
    'Humidity Percent',
    ['sybmol'] #labels
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
    TEMP_CHANGE_COUNT.labels(sensorUnit.symbol).inc()
    TEMP_HIST.labels(sensorUnit.symbol).observe(sensorValue)
    ## TEMP_GAUGE.inc()      # Increment by 1
    ## TEMP_GAUGE.dec(10)    # Decrement by given value
    TEMP_GAUGE.labels(sensorUnit.symbol).set(sensorValue)   # Set to a given value


def onHumidityChange(self, sensorValue, sensorUnit):
    # print("SensorValue: " + str(sensorValue) + " " + str(sensorUnit.symbol))
    HUMIDITY_CHANGE_COUNT.labels(sensorUnit.symbol).inc()
    HUMIDITY_HIST.labels(sensorUnit.symbol).observe(sensorValue)
    HUMIDITY_GAUGE.labels(sensorUnit.symbol).set(sensorValue)   # Set to a given value

if __name__ == '__main__':
    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput1 = VoltageRatioInput()

    voltageRatioInput0.setIsHubPortDevice(True)
    voltageRatioInput0.setHubPort(0)
    voltageRatioInput0.setDeviceSerialNumber(622942)

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
