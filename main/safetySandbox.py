from djitellopy import Tello
import csv
import pandas as pd
from pathlib import Path
import time

# Connect to Tello Drone
telloOne = Tello()
telloOne.connect()

# Conditional Statements to run through the static telemetry checks
# In the main code base, will likely use the get methods directly rather than recreating them
flag = False
if telloOne.telemtry_battery() < 50:
    flag = False
elif telloOne.telemetry_barometer() > 20:
    flag = False
elif telloOne.telemtry_hightemp() > 75:
    flag = False
elif telloOne.telemetry_avgtemp() > 60:
    flag = False
elif telloOne.telemetry_wifi_strength() < 25:
    flag = False
else:
    flag = True

telloOne.launch(flag)  # called launch function with flag input

# Creating list of status variables
column_list = ["Time (s)", "Average Temp(C)", "Highest Temp(C)", "Battery Charge"]
data = [[] for x in range(len(column_list))]

while telloOne.get_battery() > 10:

    telloOne.move_forward(30)
    telloOne.get_status()
    telloOne.rotate_clockwise(180)
    telloOne.get_status()
    telloOne.move_forward(30)
    telloOne.get_status()
    telloOne.rotate_clockwise(180)
    telloOne.get_status()

    if telloOne.get_battery() < 10:
        break

telloOne.land()

df = pd.DataFrame(list, columns = column_list)
filepath = Path("C:\\Users\\prestokp\\OneDrive\\College Career\\Senior Year Two\\MDS Capstone\\Data\\FlightData.csv")
filepath.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(filepath)

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

# Creation of takeoff function that takes in the flag value (RIP Migos Takeoff 11/1/22)
def launch(flag):
    if flag == True:
        telloOne.set_speed(100) #set speed to 100 cm/s
        telloOne.streamon()
        telloOne.takeoff()

def get_status(data):
    data[0].append(time.time()) # appends time to list
    data[1].append(telloOne.get_temperature()) # appends average temp to list
    data[2].append(telloOne.get_highest_temperature()) # appends highest temperature to list
    data[3].append(telloOne.get_battery()) # appends battery charge to list
    data[4].append(telloOne.telemetry_wifi_strength()) # appends the Wi-Fi SNR value to list



