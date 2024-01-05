from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import time

def onSensorChange(self, sensorValue, sensorUnit):
	print("SensorValue: " + str(sensorValue))
	print("SensorUnit: " + str(sensorUnit.symbol))
	print("----------")

def main():
	voltageRatioInput0 = VoltageRatioInput()
	voltageRatioInput1 = VoltageRatioInput()

	voltageRatioInput0.setIsHubPortDevice(True)
	voltageRatioInput0.setHubPort(0)
	voltageRatioInput0.setDeviceSerialNumber(622942)

	voltageRatioInput1.setIsHubPortDevice(True)
	voltageRatioInput1.setHubPort(1)
	voltageRatioInput1.setDeviceSerialNumber(622942)

	voltageRatioInput0.setOnSensorChangeHandler(onSensorChange)
	voltageRatioInput1.setOnSensorChangeHandler(onSensorChange)

	voltageRatioInput0.openWaitForAttachment(5000)
	voltageRatioInput1.openWaitForAttachment(5000)

	# Sensor Types: SENSOR_TYPE_1125_HUMIDITY, SENSOR_TYPE_1125_TEMPERATURE
	voltageRatioInput0.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1125_TEMPERATURE)
	voltageRatioInput1.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1125_HUMIDITY)

	try:
		input("Press Enter to Stop\n")
	except (Exception, KeyboardInterrupt):
		pass

	voltageRatioInput0.close()

main()
