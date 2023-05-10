from drone import Drone
from behaviors.behavior import behavior1

alpha = Drone(identifier = 'alpha',behavior = behavior1())
# alpha.operate()

alpha.connect_to_wifi('TP-Link_382E','84662019')

