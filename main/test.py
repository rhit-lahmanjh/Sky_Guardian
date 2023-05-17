import keyboard as key
from configparser import ConfigParser


repo_properties = ConfigParser()
repo_properties.read("main\\repo.properties")


while True:
    if key.is_pressed('1'):
        if key.is_pressed(repo_properties.get("all","D1_LAND_KEY")):
            print("pressed")

