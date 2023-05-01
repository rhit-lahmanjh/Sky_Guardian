from drone import Drone
from behaviors.behavior import behavior1

alpha = Drone(identifier = 'chuck',behavior = behavior1())

alpha.connect_to_wifi('TP-Link_382E','84662019')

