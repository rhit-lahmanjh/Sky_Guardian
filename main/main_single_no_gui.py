from drone import Drone
from behaviors.behavior import behavior1
import numpy as np
import threading
import time

#this shoud only be run when directly connected to the drone's wifi, rather than through a router
beta = Drone(identifier = 'beta',behavior = behavior1())

beta.operate()
