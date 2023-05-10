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
alpha_vs_port = 11111

#beta specific
betaIP = '192.168.0.248'
betaCmdPort = 8891
betaStatePort = 8892
beta_vs_port = 11112


# alpha = Drone(identifier = 'alpha',behavior = behavior1(),tello_ip=alphaIP,control_udp_port=alphaCmdPort,state_udp_port=alphaStatePort, vs_udp_port=alpha_vs_port)
beta = Drone(identifier = 'beta',behavior = behavior1(),tello_ip=betaIP,control_udp_port=betaCmdPort,state_udp_port = betaStatePort, vs_udp_port=beta_vs_port)

threads = []
# alpha_thread = threading.Thread(target=alpha.operate)
# threads.append(alpha_thread)
# alpha_thread.start()

beta_thread = threading.Thread(target=beta.operate)
threads.append(beta_thread)
beta_thread.start()
