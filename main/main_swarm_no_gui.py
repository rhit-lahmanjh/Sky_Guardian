from drone import Drone
from behaviors.behavior import behavior1
import numpy as np
import threading
from swarm import Swarm
import time as t
from configparser import ConfigParser
from device_info_reader import read_device_data

#device IDs
device_data = read_device_data()

#extra settings
repo_properties = ConfigParser()
repo_properties.read("main\\repo.properties")

#alpha specific
alphaIP = device_data.get("DRONE1_IP")
alphaCmdPort = repo_properties.getint('no_edit',"DRONE1_COMMAND_PORT")
alphaStatePort = repo_properties.getint('no_edit',"DRONE1_STATE_PORT")
alpha_vs_port = repo_properties.getint('no_edit',"DRONE1_VIDEO_PORT")

#beta specific
betaIP = device_data.get("DRONE2_IP")
betaCmdPort = repo_properties.getint('no_edit',"DRONE2_COMMAND_PORT")
betaStatePort = repo_properties.getint('no_edit',"DRONE2_STATE_PORT")
beta_vs_port = repo_properties.getint('no_edit',"DRONE2_VIDEO_PORT")


alpha = Drone(identifier = 'alpha',behavior=behavior1(), tello_ip=alphaIP,control_udp_port=alphaCmdPort,state_udp_port=alphaStatePort, vs_udp_port=alpha_vs_port,swarm=True)
beta = Drone(identifier = 'beta',behavior=behavior1(), tello_ip=betaIP,control_udp_port=betaCmdPort,state_udp_port=betaStatePort, vs_udp_port=beta_vs_port,swarm=True)

swarm = Swarm(alpha,beta)

swarm.operate()