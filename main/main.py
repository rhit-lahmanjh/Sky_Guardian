from drone import Drone
from behaviors.behavior import behavior1

drone1 = Drone(identifier = 'chuck',behavior = behavior1())
drone1.operate()