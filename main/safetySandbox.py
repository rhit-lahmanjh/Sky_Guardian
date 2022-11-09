from djitellopy import Tello
import csv
import pandas as pd
from pathlib import Path
import time

# Connect to Tello Drone
telloOne = Tello()
telloOne.connect()

print("Battery Percent (%): " + str(telloOne.get_battery()))
print("Absolute Height (cm): " + str(telloOne.get_barometer()))
print("Highest Temp (C):" + str(telloOne.get_highest_temperature()))
print("Average Temp (C): " + str(telloOne.get_temperature()))
print("Signal Noise Ratio (dB): " + telloOne.query_wifi_signal_noise_ratio())

# Conditional Statements to run through the static telemetry checks
# In the main code base, will likely use the get methods directly rather than recreating them
flag = False
if telloOne.get_battery() < 50:
    flag = False
elif telloOne.get_barometer() > 100000:
    flag = False
elif telloOne.get_highest_temperature() > 100:
    flag = False
elif telloOne.get_temperature() > 100:
    flag = False
else:
    flag = True

if flag == True: # called launch function with flag input
    print("Launch success")
    time.sleep(1)
    telloOne.streamon()
    time.sleep(1)
    telloOne.takeoff()
    time.sleep(1)
    telloOne.set_speed(100)
    time.sleep(5)

    telloOne.move_up(300)
    time.sleep(1)

    # Creating list of status variables
    column_list = ["Time (s)", "Average Temp(C)", "Highest Temp(C)", "Battery Charge", "Wi-Fi SNR"]
    data = []

    time.sleep(1)
    while telloOne.get_battery() > 10:

        telloOne.move_forward(300)
        data.append([time.time(), telloOne.get_temperature(), telloOne.get_highest_temperature(), telloOne.get_battery(),
             telloOne.query_wifi_signal_noise_ratio()])  # appends time to list
        time.sleep(1)

        telloOne.rotate_clockwise(180)
        data.append([time.time(),telloOne.get_temperature(), telloOne.get_highest_temperature(), telloOne.get_battery(),
                    telloOne.query_wifi_signal_noise_ratio()])  # appends time to list
        time.sleep(1)

        telloOne.move_forward(300)
        data.append([time.time(), telloOne.get_temperature(), telloOne.get_highest_temperature(), telloOne.get_battery(),
             telloOne.query_wifi_signal_noise_ratio()])  # appends time to list
        time.sleep(1)

        telloOne.rotate_clockwise(180)
        data.append([time.time(), telloOne.get_temperature(), telloOne.get_highest_temperature(), telloOne.get_battery(),
             telloOne.query_wifi_signal_noise_ratio()])  # appends time to list
        time.sleep(1)

        time.sleep(1)
        if telloOne.get_battery() < 10:
            break

    df = pd.DataFrame(data, columns=column_list)
    filepath = Path(
        "C:\\Users\\prestokp\\OneDrive\\College Career\\Senior Year Two\\MDS Capstone\\Data\\FlightData.csv")
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath)

    print("Battery Percent (%): " + telloOne.get_battery())
    print("Absolute Height (cm): " + telloOne.get_barometer())
    print("Highest Temp (C):" + telloOne.get_highest_temperature())
    print("Average Temp (C): " + telloOne.get_temperature())
    print("Signal Noise Ratio (dB): " + telloOne.query_wifi_signal_noise_ratio())

    time.sleep(1)
    telloOne.streamoff()
    telloOne.land()

if flag == False:
    print("Launch failed")

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
    data[0].append(time.time())  # appends time to list
    data[1].append(telloOne.get_temperature())  # appends average temp to list
    data[2].append(telloOne.get_highest_temperature())  # appends highest temperature to list
    data[3].append(telloOne.get_battery())  # appends battery charge to list
    data[4].append(telloOne.query_wifi_signal_noise_ratio())  # appends the Wi-Fi SNR value to list


