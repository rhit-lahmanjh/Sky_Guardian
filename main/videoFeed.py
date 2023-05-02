#!/bin/env python
from email.mime import image
from drone import Drone
from refresh_tracker import State
import flet as ft
import djitellopy
import socket
import time
import cv2
import base64
import threading
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


# tello_address = ('192.168.10.1', 8889)
# local_address = ('', 9000)


# CV2 Window 
class Countdown(ft.UserControl):
    def __init__(self, drone:Drone):
        super().__init__()
        self.drone = drone

    def did_mount(self):
        self.update_timer()

    def update_timer(self):
        while True:
            returned, frame = [self.drone.sensoryState.returnedImage, self.drone.sensoryState.image]

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
    drone1 = Drone(identifier = 'test',behavior = behavior1())
    
    # Setting up threading
    threads = []
    FSM_thread = threading.Thread(target=drone1.operate)
    threads.append(FSM_thread)
    FSM_thread.start()

    d1_stream = ft.Card(
            elevation=30,
            content=ft.Container(
                bgcolor=ft.colors.WHITE24,
                padding=10,
                border_radius = ft.border_radius.all(20),
                content=ft.Column([
                    Countdown(drone1),
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
                    Countdown(drone1),
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
