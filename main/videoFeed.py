#!/bin/env python
from email.mime import image
from drone import Drone
from refresh_tracker import State
import flet as ft
import socket
import time
import cv2
import base64
import threading
import logging
from flet import (
    Column,
    Container,
    ElevatedButton,
    Page,
    Row,
    Text,
    border_radius,
    colors,
    CrossAxisAlignment,
)
from behaviors.behavior import behavior1
from sensoryState import SensoryState
from swarm import Swarm
import time as t

logging.getLogger("flet_core").setLevel(logging.FATAL)

# CV2 Window 
class Countdown(ft.UserControl):
    def __init__(self, drone:Drone):
        super().__init__()
        self.drone = drone

    def did_mount(self):
        self.running = True
        self.th = threading.Thread(target=self.update_timer, args=(), daemon=True)
        self.th.start()

    def will_unmount(self):
        self.running = False

    def update_timer(self):
        while True:
            returned, frame = [self.drone.sensoryState.returnedImage, self.drone.sensoryState.image]

            # print(f"not returned from drone {self.drone.identifier}")
            if returned:
                _, im_arr = cv2.imencode('.png', frame)
                im_b64 = base64.b64encode(im_arr)
                self.img.src_base64 = im_b64.decode("utf-8")
            self.update()

    def build(self):
        self.img = ft.Image(
            border_radius=ft.border_radius.all(20)
        )
        return self.img    

        
def main(page: ft.Page):
    # drone connection
    # alpha specific
    alphaIP = '192.168.0.140'
    alphaCmdPort = 8889
    alphaStatePort = 8890
    alpha_vs_port = 11111

    #beta specific
    betaIP = '192.168.0.248'
    betaCmdPort = 8891
    betaStatePort = 8892
    beta_vs_port = 11112
    drone1 = Drone(identifier = 'alpha',behavior = behavior1(),tello_ip=alphaIP,control_udp_port=alphaCmdPort,state_udp_port=alphaStatePort, vs_udp_port=alpha_vs_port)
    drone2 = Drone(identifier = 'beta',behavior = behavior1(),tello_ip=betaIP,control_udp_port=betaCmdPort,state_udp_port = betaStatePort, vs_udp_port=beta_vs_port)

    swarm = Swarm(drone1,drone2)

    # Setting up threading
    threads = []
    FSM_thread = threading.Thread(target=swarm.operate)
    threads.append(FSM_thread)
    FSM_thread.start()

    page.title = "inTellogence"

    #handle stopping
    def disconnect_swarm(self):
        swarm.turnOff = True
        
    def window_event(e):
        if e.data == "close":
            print("Disconnecting")
            disconnect_swarm()
            t.sleep(3)


    page.on_window_event = window_event

    d1_stream = ft.Card(
            elevation=30,
            content=ft.Container(
                bgcolor=ft.colors.WHITE24,
                padding=10,
                border_radius = ft.border_radius.all(20),
                content=ft.Column([
                    Countdown(swarm.drone2),
                    ft.Text("Drone 1",
                         size=20, weight="bold",
                         color=ft.colors.WHITE),
                ]
                ),
            )
    )

    d2_stream = ft.Card(
            elevation=30,
            content=ft.Container(
                bgcolor=ft.colors.WHITE24,
                padding=10,
                border_radius = ft.border_radius.all(20),
                content=ft.Column([
                    Countdown(swarm.drone1),
                    ft.Text("Drone 2",
                         size=20, weight="bold",
                         color=ft.colors.WHITE),
                ]
                ),
            )
    )

    page.add(
        d1_stream,
        d2_stream
    )

ft.app(target=main)
