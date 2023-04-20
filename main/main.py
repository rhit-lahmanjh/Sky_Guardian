from drone import Drone
from behaviors.behavior import behavior1
import numpy as np
import time

alphaIP = '192.168.0.140'
local1_address = ('192.168.0.245',9010)



alpha = Drone(identifier = 'chuck',behavior = behavior1(),)
alpha.operate()

# dir = np.array([[50],[0],[0],[0]])

# drone1.takeoff()
# drone1.moveDirection(dir)
# time.sleep(5)
# drone1.hover()
# drone1.land()