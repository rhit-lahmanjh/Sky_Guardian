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

    page.title = "Drone Basic Functions"

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

    # grabs list of possible reaction objects
    object_list = [obj.name for obj in vision_class]

    reaction_data = ["Flip", "Bob", "Pause", "Follow", "Run"]

    # make Class that allows the user to select an object and Reaction
    class ReactionInput(ft.UserControl):
        def __init__(self, drone, name):
            super().__init__()
            self.name = name
            self.drone = drone
            self.selectedObject = NULL
            self.selectedBehavior = NULL
            self.badIcon = ft.Icon(name=ft.icons.QUESTION_MARK, color=ft.colors.BLUE_GREY_300, size=30)
            self.goodIcon = ft.Icon(name=ft.icons.CHECK, color=ft.colors.GREEN_300, size=30)
            self.itemSelected = FALSE
            self.behaviorSelected = FALSE
            self.add_reaction_button = ft.FilledButton(icon=icons.ADD, text = "Add new reaction", height = 30, on_click=self.createReactions)

            self.reaction_lists = [
                self.add_reaction_button
            ]

        def build(self):
            self.b = ft.FilledButton(text="Submit", on_click=self.button_clicked, icon=self.badIcon)
            self.dd = ft.Dropdown(
                width=300,
                options=[],
                label = ft.Text("Select Reaction")
            )
            
            for item in reaction_data:
                self.dd.options.append(ft.dropdown.Option(str(item)))

            self.txtsearch = TextField(label="Input object from COCO dataset",on_change=self.searchnow, on_submit=self.searchnow)
            
            return ft.Card( 
                    content=ft.Container(
                    content=ft.Column(
                    [
                        self.dd,
                        self.txtsearch,
                        self.b
                    ]
                    ),
                    width=400,
                    padding=10,
                    )
        )
            
        def searchnow(self, e):

            self.mysearch = e.control.value

            for item in object_list:
                    if self.mysearch == item:
                        self.selectedObject = item
                        self.itemSelected = TRUE
                        print(self.itemSelected)
            
            self.b.icon = self.badIcon
            self.itemSelected = FALSE
            self.behaviorSelected == self.dd

            page.update()
                
        def button_clicked(self, e):
            if(self.itemSelected == TRUE):
                self.b.icon = self.goodIcon
            page.update()

        def getSelectedObject(self):
            return self.selectedObject

        def getSelectedBehavior(self):
            return self.selectedBehavior
            

    drone1_launch_button = ft.Container(
            content=ft.TextButton(text=""),
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
                content=ft.Column(
                    drone1_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
        ]
    )

    drone2_launch_button = ft.Container(
            content=ft.TextButton(text=""),
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
                content=ft.Column(
                    drone2_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER)
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
                            ReactionInput(swarm.drone1),
                        # User input control for Reactions & Behaviors
                    ]
                ),
                width=400,
                height=250,
            ),
        ft.Text("Drone 2"),
        ft.Container(
                content=ft.Row(
                    [
                        # command buttons for Launch and Land
                        drone2_column,

                        ReactionInput(swarm.drone2),
                        # User input control for Reactions & Behaviors
                    ]
                ),
                width=400,
                height=250,
            ),
    )

ft.app(target=main, assets_dir="assets")
cv2.destroyAllWindows()