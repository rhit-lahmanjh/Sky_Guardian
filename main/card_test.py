import itertools
import sys
from drone import Drone
from pickle import FALSE, TRUE
import flet as ft
from asyncio.windows_events import NULL
from tkinter import dialog, font
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

sys.path.append('../')

def main(page: ft.Page):
    page.title = "Card Example"
    page.fonts = {
        "Space": "assets\space-grotesk.regular.ttf",
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf"
    }
    page.theme = ft.Theme(font_family="Space")

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

    # reaction_list = []

    # def populate_reaction_list():
    #     for br in behavior1.blockingReactions:
    #         reaction_list.append(
    #             ft.Container(
    #                 content=ft.Text(value = br.identifier)
    #             )
    #         )

    #     for mr in behavior1.movementReactions:
    #         reaction_list.append(
    #             ft.Container(
    #                 content=ft.Text(value = mr.identifier)
    #             )
    #         )
        
    #     return reaction_list

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
                # val = dialog_text.value

                # for item in object_list:
                #     if val in item:
                #         self.selectedObject = item
                #         self.objectIsSelected = TRUE

                # if dialog_text.value == "" or self.objectIsSelected == FALSE:
                #     create_button.disabled = TRUE
                # else:
                #     create_button.disabled = FALSE

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

    def delete_reaction(e):
        print("DELETE")
        page.update()

    def clear_all_reactions(e):
        print("CLEAR")
        page.update()

    page.add(
        ReactionInput(drone1)
    )

ft.app(target=main)
