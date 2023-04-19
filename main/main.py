from drone import Drone
from behaviors.behavior import behavior1
import numpy as np
import time

drone1 = Drone(identifier = 'chuck',behavior = behavior1())
drone1.operate()

# dir = np.array([[50],[0],[0],[0]])

# drone1.takeoff()
# drone1.moveDirection(dir)
# time.sleep(5)
# drone1.hover()
# drone1.land()