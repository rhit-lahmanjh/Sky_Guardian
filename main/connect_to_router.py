from behaviors.behavior import behavior1
from drone import Drone
from device_info_reader import read_device_data

device_data = read_device_data()

drone_to_connect = Drone(identifier = 'x')

drone_to_connect.connect_to_wifi(device_data.get("ROUTER_SSID"),device_data.get("ROUTER_PASSWORD"))

