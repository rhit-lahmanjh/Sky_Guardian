#!/bin/env python
from asyncio.windows_events import NULL
from pickle import FALSE, TRUE
from tkinter import font
from drone import (Drone, State)
from behaviors.behavior import behavior1
from reactions.reaction import bobOnScissors, flipOnBanana, followCellPhone, followObject, runFromBanana
from reactions.reaction import blockingReaction, movementReaction
import flet as ft
import djitellopy
import socket
import time
import logging
import numpy as np
from yolo_classes import vision_class
import cv2
import base64
import threading
from flet import * 
from sensory_state import SensoryState
from swarm import Swarm
        
logging.getLogger("flet_core").setLevel(logging.FATAL)

def main(page: ft.Page):
    page.fonts = {
        "Space": "assets\space-grotesk.regular.ttf",
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf"
    }

    page.theme = Theme(font_family="Space")
    page.theme_mode = ft.ThemeMode.LIGHT
    object_list = [obj.name for obj in vision_class]
    reaction_data = ["Flip on Banana", "Bob on Scissors", "Run from Banana", "Run from Object"]

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

    page.title = "inTellogence Main Dashboard"

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
        # opening the file in read mode

    # Creating Drone Manipulation Functions
    drone1_launch_button = ft.Container(
            content=ft.TextButton(text=""),
            image_src="assets\drone_launch.png",
            width=100,
            height=100,
            padding=padding.only(left=10, right=5, bottom=15),
            on_click=drone1_launch
        )

    drone1_land_button = ft.Container(
            content=ft.TextButton(text=""),
            image_src="assets\drone_land.png",
            width=100,
            height=100,
            padding=padding.only(left=10, right=5),

            on_click=drone1_land
        )

    drone1_items = [
        drone1_launch_button, ft.Text("LAUNCH", font_family="Space"), 
        drone1_land_button, ft.Text("LAND",font_family="Space")
    ]

    drone1_column = ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    drone1_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ),
        ]
    )

    drone2_launch_button = ft.Container(
            content=ft.TextButton(text=""),
            image_src="assets\drone_launch.png",
            width=100,
            height=100,

            on_click=drone2_launch
        )

    drone2_land_button = ft.Container(
            content=ft.TextButton(text=""),
            image_src="assets\drone_land.png",
            width=100,
            height=100,

            on_click=drone2_land
        )

    drone2_items = [
        drone2_launch_button, ft.Text("LAUNCH", font_family="Space"), 
        drone2_land_button, ft.Text("LAND",font_family="Space")
    ]
    
    drone2_column = ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    drone2_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ),
        ]
    )

    ## REACTION INPUT CLASS
    class ReactionInput(ft.UserControl):
        def __init__(self, drone:Drone):
            super().__init__()
            self.drone = drone
            self.reactionSelected = None
            self.selectedObject = None
            self.objectIsSelected = False
            self.reaction_data = ["Follow Object", "Flip On Banana", "Bob on Scissors", "Follow Cell Phone", "Run From Banana"]
            self.reactionList = drone.behavior.blockingReactions + drone.behavior.movementReactions
            self.items = []

        def build(self):
            # We allow the user to create/set new reations using an alert dialog
            # Dialog functions
            def open_dlg_modal(e):
                page.dialog = self.dlg_modal
                self.dlg_modal.open = True
                page.update()

            def close_dlg(e):
                self.dlg_modal.open = False
                page.update()

            def textfield_change(e):
                if dialog_text.value == "":
                    create_button.disabled = True
                else:
                    create_button.disabled = False
                self.page.update()
            
            ## converting given Reaction string to Reaction object
            def convertStringToReaction(string):
                if string == 'Follow Object':
                    return followObject(self.selectedObject)
                elif string == 'Flip on Banana': 
                    return flipOnBanana()
                elif string == 'Bob on Scissors': 
                    return bobOnScissors()
                elif string == 'Follow Cell Phone': 
                    return followCellPhone()
                elif string =='Run From Banana': 
                    return runFromBanana()
                else:
                    "Invalid input"

            def add_selected_reaction_to_behavior(e):
                try:
                    r = convertStringToReaction(self.reactionSelected)
                    self.drone.behavior.add_reaction(r)
                    self.reactionList.append(r)
                    col.controls.append(
                        ReactionComponent(self.reactionSelected, r)
                    )
                    card.update()
                    page.update()
                except:
                    print("Error not found")

                page.update()
                close_dlg(e)

            def toggle_create_button(e):
                create_button.disabled=False
                if(self.dropdown_menu.value == "Run from Object"):
                    self.reactionSelected = "Run from " + self.selectedObject
                self.reactionSelected = self.dropdown_menu.value
                self.dlg_modal.update()

            # dialog components
            self.dropdown_menu = ft.Dropdown(
                    width=300,
                    options=[],
                    label = "Select Reaction",
                    on_change=toggle_create_button
            )
                
            for item in reaction_data:
                self.dropdown_menu.options.append(ft.dropdown.Option(str(item)))

            create_button = ElevatedButton(text="Create", bgcolor=colors.BLUE_200, on_click=add_selected_reaction_to_behavior, disabled=True)

            dialog_text = ft.TextField(label="Input Object from COCO dataset", on_change=textfield_change)

            ## dialig box to add reaction
            self.dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Add new reaction"),
                content=Column([
                            self.dropdown_menu,
                            Container(content=dialog_text,
                            padding=padding.symmetric(horizontal=5)),

                            Row([
                                ElevatedButton(text="Cancel", on_click=close_dlg),
                                create_button
                                ], 
                            alignment="spaceBetween"
                            )
                            ], tight=True, alignment="center"
                        ),
                on_dismiss=lambda e: print("Modal dialog dismissed!")
            )

            ## deleting a reaction
            def delete_reaction(e):
                print("Deleting...")
                for rc in self.items:
                    if rc.selected == True:
                        print(rc.reaction.identifier + " is being deleted")
                        self.items.remove(rc)
                        self.reactionList.remove(rc.reaction)
                        self.drone.behavior.remove_reaction(rc.reaction.identifier)
                    card.update()
                page.update()

            add_reaction_button = ft.IconButton(icon=ft.icons.ADD, icon_size = 30, height = 50, on_click=open_dlg_modal)
            delete_reaction_button = ft.IconButton(icon=ft.icons.DELETE, icon_size = 30, height = 50, on_click=delete_reaction)

            class ReactionComponent(ft.UserControl):
                def __init__(self, name:str, reaction):
                    super().__init__()
                    self.name = name
                    self.reaction = reaction
                    self.selected = False
                
                def build(self):
                    def toggle_container(e):
                        if self.selected == True: 
                            self.selected = False
                            displayBox.bgcolor = ft.colors.BLUE
                            print(self.selected)
                        
                        else:
                            self.selected = True
                            displayBox.bgcolor =  ft.colors.AMBER
                            print(self.selected)

                        displayBox.update()
                        self.page.update()

                    displayBox = ft.Container(
                            content=ft.Text(value=self.name),
                            alignment=ft.alignment.center,
                            width=400,
                            height=30,
                            bgcolor=ft.colors.BLUE,
                            border_radius=ft.border_radius.all(5),
                            on_click=toggle_container
                    )
                    
                    return displayBox

            def updatedReactionList()-> list:
                print("Updated Reaction List")
                items = []
                for i in range(len(self.reactionList)):
                    r = ReactionComponent(self.reactionList[i].identifier, self.reactionList[i])
                    items.append(r)
                self.items = items
                return items

            col = ft.Column(spacing=5, controls=updatedReactionList())

            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                controls = [
                                    ft.Text("Reactions", style=ft.TextThemeStyle.TITLE_MEDIUM), 
                                    add_reaction_button,
                                    delete_reaction_button,
                                ],
                                alignment=ft.MainAxisAlignment.START
                            ), 
                            col
                        ]
                    ),
                    width=400,
                    height = 200,
                    padding=10,
                )
            )

            return card
        
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

    d1_stream = ft.Card(
            elevation=30,
            content=ft.Container(
                bgcolor=ft.colors.WHITE24,
                padding=10,
                border_radius = ft.border_radius.all(20),
                content=ft.Column([
                    Countdown(swarm.drone1),
                    ft.Text("Drone 1",
                    size=20, weight="bold",
                    color=ft.colors.WHITE),
                ]
                ),
            )
            # ,height=400
    )

    d2_stream = ft.Card(
            elevation=30,
            content=ft.Container(
                bgcolor=ft.colors.WHITE24,
                padding=10,
                border_radius = ft.border_radius.all(20),
                content=ft.Column([
                    Countdown(swarm.drone2),
                    ft.Text("Drone 2",
                    size=20, weight="bold",
                    color=ft.colors.WHITE),
                ]
                ),
            )
            # ,height=400
    )

  

    page.add(
        ft.Container(
                content=ft.Row([
                        ft.Text("Drone 1", style=ft.TextThemeStyle.TITLE_LARGE), 

                        # command buttons for Launch and Land
                        drone1_column,
                        # command buttons for Hover, Scan, Wander, and Drift
                        ft.Column([
                            ft.FilledButton(text="Hover", on_click=drone1_hover),
                            # ft.FilledButton(text="Scan", on_click = drone1_scan),
                            ft.FilledButton(text="Wander", on_click = drone1_wander),
                            ft.FilledButton(text="Drift", on_click = drone1_drift),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        # User input control for Reactions & Behaviors
                        ReactionInput(swarm.drone1),
                        # d1_stream
                    ]
                ),
                width=400,
                height=250,
                margin = margin.only(bottom=25, left=20)
            ),
        ft.Container(
                content=ft.Row(
                    [
                        ft.Text("Drone 2", style=ft.TextThemeStyle.TITLE_LARGE), 

                        # command buttons for Launch and Land
                        drone2_column,

                        # command buttons for Hover, Scan, Wander, and Drift
                        ft.Column([
                            ft.FilledButton(text="Hover", on_click=drone2_hover),
                            # ft.FilledButton(text="Scan", on_click = drone2_scan),
                            ft.FilledButton(text="Wander", on_click = drone2_wander),
                            ft.FilledButton(text="Drift", on_click = drone2_drift),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        
                        # User input control for Reactions & Behaviors
                        ReactionInput(swarm.drone2),
                        # d2_stream
                    ]
                ),
                width=400,
                height=250,
                margin=margin.only(top=80, left=20)
            ),
    )

ft.app(target=main, assets_dir="assets")
cv2.destroyAllWindows()