#!/bin/env python
from asyncio.windows_events import NULL
from pickle import FALSE, TRUE
from tkinter import font
from drone import (Drone, State)
from behaviors.behavior import behavior1
import flet as ft
import djitellopy
import socket
import time
import logging
import numpy as np
from yoloClasses import vision_class
import cv2
import base64
import threading
from flet import * 
from gui_modules.reaction_board import ReactionInput
from gui_modules.reaction_component import ReactionComponent
from sensoryState import SensoryState
from swarm import Swarm
        
logging.getLogger("flet_core").setLevel(logging.FATAL)

def main(page: ft.Page):
    page.fonts = {
        "Space": "assets\space-grotesk.regular.ttf",
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf"
    }

    page.theme = Theme(font_family="Space")

    # drone connection
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
    drone1 = Drone(identifier = 'alpha',behavior = behavior1(),tello_ip=alphaIP,control_udp_port=alphaCmdPort,state_udp_port=alphaStatePort, vs_udp_port=alpha_vs_port)
    drone2 = Drone(identifier = 'beta',behavior = behavior1(),tello_ip=betaIP,control_udp_port=betaCmdPort,state_udp_port = betaStatePort, vs_udp_port=beta_vs_port)

    swarm = Swarm(drone1,drone2)

    # Setting up threading
    threads = []
    FSM_thread = threading.Thread(target=swarm.operate)
    threads.append(FSM_thread)
    FSM_thread.start()

    page.title = "inTellogence Dashboard"

    # Button functions
    def drone1_launch(e):
        swarm.drone1.opState = State.Takeoff
        page.update()
    
    def drone2_launch(e):
        swarm.drone2.opState = State.Takeoff
        page.update()

    def drone1_land(e):
        swarm.drone1.opState = State.Land
        page.update()
    
    def drone2_land(e):
        swarm.drone2.opState = State.Land
        page.update()

    def drone1_hover(e):
        swarm.drone1.opState = State.Hover
        page.update()
    
    def drone2_hover(e):
        swarm.drone1.opState = State.Hover
        page.update()

    def drone1_scan(e):
        swarm.drone1.opState = State.Scan
        page.update()
    
    def drone2_scan(e):
        swarm.drone2.opState = State.Scan
        page.update()

    def drone1_wander(e):
        swarm.drone1.opState = State.Wander
        page.update()
    
    def drone2_wander(e):
        swarm.drone2.opState = State.Wander
        page.update()
    
    def drone1_drift(e):
        swarm.drone1.opState = State.Drift
        page.update()
    
    def drone2_drift(e):
        swarm.drone2.opState = State.Drift
        page.update()
    
    def order66(e):
        swarm.drone1.opState = State.Hover
        swarm.drone2.opState = State.Hover
        page.update()        

    ## Attaching images to the Launch and Land buttons

    drone1_launch_button = ft.Container(
            image_src="assets\drone_launch.png",
            width=100,
            height=100,
            padding=padding.only(left=10, right=5, bottom=15),

            on_click=drone1_launch
        )

    drone1_land_button = ft.Container(
            image_src="assets\drone_land.png",
            width=100,
            height=100,
            padding=padding.only(left=10, right=5),
            on_click=drone1_land
        )

    drone1_items = [
        drone1_launch_button, ft.Text("LAUNCH", font_family="Space"), drone1_land_button, ft.Text("LAND",font_family="Space")
    ]

    drone1_column = ft.Column(
        [
            ft.Container(
                content=ft.Row (
                    ft.Column(
                    drone1_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                    ft.Column(
                        ft.OutlinedButton(text="Hover", on_click=drone1_hover),
                        ft.OutlinedButton(text="Scan", on_click = drone1_scan),
                        ft.OutlinedButton(text="Wander", on_click = drone1_wander),
                        ft.OutlinedButton(text="Drift", on_click = drone1_drift)
                    )
                )
            ),
        ]
    )

    drone2_launch_button = ft.Container(
            image_src="assets\drone_launch.png",
            width=100,
            height=100,
            padding=padding.only(left=10, right=5, bottom=15),

            on_click=drone2_launch
        )

    drone2_land_button = ft.Container(

            image_src="assets\drone_land.png",
            width=100,
            height=100,
            padding=padding.only(left=10, right=5),
            on_click=drone2_land
        )

    drone2_items = [
        drone2_launch_button, ft.Text("LAUNCH", font_family="Space"), drone2_land_button, ft.Text("LAND",font_family="Space")
    ]

    drone2_column = ft.Column(
        [
            ft.Container(
                content=ft.Row (
                    ft.Column(
                    drone2_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                    ft.Column(
                        ft.OutlinedButton(text="Hover", on_click=drone2_hover),
                        ft.OutlinedButton(text="Scan", on_click = drone2_scan),
                        ft.OutlinedButton(text="Wander", on_click = drone2_wander),
                        ft.OutlinedButton(text="Drift", on_click = drone2_drift)
                    )
                )
            ),
        ]
    )

    page.add(
        ft.Text("Drone 1"),
        ft.Container(
                content=ft.Row(
                    [
                        # command buttons for Launch and Land
                        drone1_column,
                        # ReactionInput(swarm.drone1),
                        # User input control for Reactions & Behaviors
                    ]
                ),
                width=400,
                height=250,
            ),
        # ft.Container(
        #         content=ft.Row(
        #             [
        #                 # command buttons for Launch and Land
        #                 drone1_column,
        #                 # drone2_column,

        #                 ReactionInput(swarm.drone1),
        #                 # ReactionInput(swarm.drone2)
        #                 # User input control for Reactions & Behaviors
        #             ]
        #         ),
        #         width=400,
        #         height=250,
        #     ),
    )

ft.app(target=main, assets_dir="assets")
cv2.destroyAllWindows()