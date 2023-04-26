from drone import Drone
from behaviors.behavior import behavior1
import numpy as np
import threading
import time

#user specific variables
joseph_local_address = '192.168.0.248'

#alpha specific
alphaIP = '192.168.0.140'
alphaCmdPort = 8889
alphaStatePort = 8890
# local1_address = ('192.168.0.245',9010)
alpha_vs_port = 11112

#beta specific
betaIP = '192.168.0.248'
betaCmdPort = 8889
# local2_address = ('192.168.0.146',9011)
beta_vs_port = 11111


alpha = Drone(identifier = 'alpha',behavior = behavior1(),tello_ip=alphaIP,control_udp_port=alphaCmdPort,vs_udp_port=alpha_vs_port)
# beta = Drone(identifier = 'beta',behavior = behavior1(),tello_ip=betaIP,control_udp_port=betaCmdPort,vs_udp_port=beta_vs_port)

# alpha.operate()


threads = []
alpha_thread = threading.Thread(target=alpha.operate)
threads.append(alpha_thread)
alpha_thread.start()

# beta_thread = threading.Thread(target=beta.operate)
# threads.append(beta_thread)
# beta_thread.start()

# dir = np.array([[50],[0],[0],[0]])

# drone1.takeoff()
# drone1.moveDirection(dir)
# time.sleep(5)
# drone1.hover()
# drone1.land()