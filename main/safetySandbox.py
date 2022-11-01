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

# Get the Wi-Fi Signal Noise Ratio (SNR) to determine the quality of the performance and speed of the Wi-Fi connection
# Good values range from 24dB to 40dB
# Returns the dB value as a Str
def telemetry_wifi_strength():
    signalStrength = telloOne.query_wifi_signal_noise_ratio()
    signalStrengthInt = int(signalStrength)
    return signalStrengthInt

# Conditional Statements to run through the static telemetry checks
# In the main code base, will likely use the get methods directly rather than recreating them
flag = False
if telemtry_battery() < 50:
    flag = False
elif telemetry_barometer() > 20:
    flag = False
elif telemtry_hightemp() > 75:
    flag = False
elif telemetry_avgtemp() > 60:
    flag = False
elif telemetry_wifi_strength() < 25:
    flag = False
else:
    flag = True

# Creation of takeoff function that takes in the flag value (RIP Migos Takeoff 11/1/22)
def launch(flag):
    if flag == True:
        telloOne.set_speed(100) #set speed to 100 cm/s
        telloOne.streamon()
        telloOne.takeoff()

launch(flag) # called launch function with flag input


