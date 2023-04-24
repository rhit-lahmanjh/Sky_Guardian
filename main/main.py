from drone import Drone
from behaviors.behavior import behavior1
import numpy as np
import time

alphaIP = '192.168.0.140'
alphaCmdPort = 8889
local1_address = ('192.168.0.245',9010)
joseph_local_address = '192.168.0.248'
alpha_vs_port = 9012

betaIP = '192.168.0.248'
betaCmdPort = 8889
local2_address = ('192.168.0.146',9011)
beta_vs_port = 9013


# alpha = Drone(identifier = 'alpha',behavior = behavior1(),tello_ip=betaIP,control_udp_port=betaCmdPort,vs_udp_port=beta_vs_port)
beta = Drone(identifier = 'beta',behavior = behavior1(),tello_ip=betaIP,control_udp_port=betaCmdPort,vs_udp_port=beta_vs_port,local_computer_IP=joseph_local_address)

beta.operate()

# dir = np.array([[50],[0],[0],[0]])

# drone1.takeoff()
# drone1.moveDirection(dir)
# time.sleep(5)
# drone1.hover()
# drone1.land()