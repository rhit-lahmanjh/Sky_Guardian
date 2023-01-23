from djitellopy import Tello
from drone import Drone
import pandas as pd
from pathlib import Path
import time
import keyboard

# Connect to Tello Drone
telloOne = Tello()
telloOne.connect()
telloOne.streamon()

def checkTelemetry():
    # Checks the battery charge before takeoff

        """print("Battery Charge: " + telloOne.get_battery())
        if telloOne.get_battery > 50:
            BatCheck = True
        else:
            BatCheck = False
            print("Battery Charge Too Low")"""

        print("Battery Charge: " + str(telloOne.get_battery()))
        if telloOne.get_battery() > 11:
            BatCheck = True
        else:
            BatCheck = False
            print("Battery Charge Too Low")

        # Checks the highest battery temperature before takeoff
        print("Highest Battery Temperature: " + str(telloOne.get_highest_temperature()))
        if telloOne.get_highest_temperature() < 100:
            TemphCheck = True
        else:
            TemphCheck = False
            print("Battery Temperature Too High")

        # Checks the baseline low temperature before takeoff
        print("Baseline Battery Temperature: " + str(telloOne.get_lowest_temperature()))
        if telloOne.get_lowest_temperature() < 90:
            TemplCheck = True
        else:
            TemplCheck = False
            print("Baseline Low Temperature Too High")

        # Turns the string SNR value into an integer
        # Checks the Wi-Fi SNR value to determine signal strength
        print("Signal Strength: " + telloOne.query_wifi_signal_noise_ratio())
        signalStrength = telloOne.query_wifi_signal_noise_ratio()
        if signalStrength != 'ok' and signalStrength != 'okay':
            signalStrengthInt = int(signalStrength)
        if signalStrength == 'ok':
            SignalCheck = True
        elif signalStrengthInt > 15:
            SignalCheck = True
        else:
            SignalCheck = False
            print("SNR below 15dB. Weak Connection")

        # Checks to make sure the pitch is not too far off
        # If the drone is too far from 0 degrees on pitch the takeoff
        # could be unsafe
        print("Pitch: " + str(telloOne.get_pitch()))
        pitch = abs(telloOne.get_pitch())
        if pitch < 10:
            pitchCheck = True
        else:
            pitchCheck = False
            print("Pitch is Off Center. Unstable takeoff or flight.")

        # Checks to make sure the roll is not too far off
        # If the drone is too far from 0 degrees on roll the takeoff
        # could be unsafe
        print("Roll: " + str(telloOne.get_roll()))
        roll = abs(telloOne.get_roll())
        if roll < 10:
            rollCheck = True
        else:
            rollCheck = False
            print("Roll is Off Center. Unstable takeoff of flight.")

        # Comment out function as needed until testing can confirm desired threshold value
        # Checks to ensure the drone is at a low enough height to ensure room during takeoff for safe ascent
        print("Height: " + str(telloOne.get_height()))
        if telloOne.get_height() < 300: #Height increases from takeoff point
            HeightCheck = True
        else:
            HeightCheck = False
            print("Drone is too High")

        # Dictionary of Boolean values to check through static telemetry
        telloOne.telemetryCheck = {"bat": BatCheck, "temph": TemphCheck, "templ": TemplCheck,
                           "SignalStrength": SignalCheck, "pitch": pitchCheck, "roll": rollCheck,
                           "height": HeightCheck}

        print("Completed Telemetry Checks")
        print(telloOne.telemetryCheck.values())
        return all(telloOne.telemetryCheck.values())

safeFlight = checkTelemetry()
if safeFlight is True:
    speed = telloOne.set_speed(100)
    print(speed)
    print("I am speed!")
    telloOne.streamoff()
    print(telloOne.get_barometer())
else:
    speed = telloOne.set_speed(50)
    print(speed)
    print("I am not safe!")
    telloOne.streamoff()



