from djitellopy import Tello
from djitellopy import TelloSwarm
from threading import Thread

# Connect to Tello Drone
telloOne = Tello()
telloOne.connect()

# Telemetry 'Get' Functions are getting static telemetry data to be used in Safety checks before the drones is allowed
# to take off

# Get the battery percentage as an int
def telemtry_battery():
    batteryCharge = telloOne.get_battery()
    return batteryCharge

# Get the highest temperature the battery is currently experiencing; returned as a float in degrees Celsius
def telemtry_hightemp():
    highTemp = telloOne.get_highest_temperature()
    return highTemp

# Get the average temperature the battery is currently experiencing; returned as a float in degrees Celsius
def telemetry_avgtemp():
    avgTemp = telloOne.get_temperature()
    return avgTemp

# Get the absolute height of the drone; absolute height is in cm
def telemetry_barometer():
    absHeight = telloOne.get_barometer()
    return absHeight



