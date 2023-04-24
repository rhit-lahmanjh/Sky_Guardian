from drone import Drone
from behaviors.behavior import behavior1

alphaIP = '192.168.0.140'
local1_address = ('192.168.0.245',9010)

alpha = Drone(identifier = 'chuck',behavior = behavior1())

alpha.connect_to_wifi('TP-Link_382E','84662019')

