from Phidget22.Phidget import *
from Phidget22.Devices.DigitalInput import *
import time

def onStateChange(self, state):
	print("State: " + str(state))

def main():
	digitalInput0 = DigitalInput()

	digitalInput0.setIsHubPortDevice(True)
	digitalInput0.setHubPort(0)

	digitalInput0.setOnStateChangeHandler(onStateChange)

	digitalInput0.openWaitForAttachment(5000)

	try:
		input("Press Enter to Stop\n")
	except (Exception, KeyboardInterrupt):
		pass

	digitalInput0.close()

main()

