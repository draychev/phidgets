import time
from Phidget22.Phidget import *
from Phidget22.Devices.HumiditySensor import *

# Create a humidity sensor object
humiditySensor = HumiditySensor()

# Set addressing parameters (if needed)
humiditySensor.setDeviceSerialNumber(123456)  # Replace with your sensor's serial number

# Open the sensor for device connections
humiditySensor.openWaitForAttachment(5000)

try:
    while True:
        # Read humidity value
        humidity = humiditySensor.getHumidity()

        # Print the humidity value
        print("Humidity:", humidity, "%")

        # Wait for a second before the next reading
        time.sleep(1)

except PhidgetException as e:
    print("Phidget error:", e)

finally:
    # Close the sensor
    humiditySensor.close()

