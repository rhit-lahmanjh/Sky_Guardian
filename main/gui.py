#!/bin/env python
from drone import (Drone, State)
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

# tello_address = ('192.168.10.1', 8889)
# local_address = ('', 9000)
        
def main(page: ft.Page):
    # drone connection
    drone1 = Drone('test')
    cap = drone1.get_video_capture()

    # Setting up threading
    threads = []
    FSM_thread = threading.Thread(target=drone1.operate)
    threads.append(FSM_thread)
    FSM_thread.start()

    page.title = "Drone Basic Functions"

    # Button functions
    def drone1_launch(e):
        print("Drone 1 State: Takeoff")
        drone1.opState = State.Takeoff
        page.update()
    
    def drone2_launch(e):
        print("Drone 2 State: Takeoff")
        # drone2.opState = State.Takeoff
        page.update()

    def drone1_land(e):
        print("Drone 1 State: Landed")
        drone1.opState = State.Landed
        page.update()
    
    def drone2_land(e):
        print("Drone 2 State: Landed")           
    #     drone2.opState = State.Landed
        page.update()

    def drone1_hover(e):
        print("Drone 1 State: Hover")  
        drone1.opState = State.Hover
        page.update()
    
    def drone2_hover(e):
        print("Drone 2 State: Hover")           
        #     drone2.opState = State.Hover
        page.update()
    
    def order66(e):
        print("Order 66")
        print("Drone 1 State: Hover")           
        print("Drone 2 State: Hover")

        drone1.opState = State.Hover
        # drone2.opState = State.Hover
        page.update()        

    # CV2 Window 
    class Countdown(ft.UserControl):
        def __init__(self):
            super().__init__()

        def did_mount(self):
            self.update_timer()

        def update_timer(self):
            while True:
                _, frame = cap.read()
                # frame = cv2.resize(frame,(400,400))
                _, im_arr = cv2.imencode('.png', frame)
                im_b64 = base64.b64encode(im_arr)
                self.img.src_base64 = im_b64.decode("utf-8")
                self.update()

        def build(self):
            self.img = ft.Image(
                border_radius=ft.border_radius.all(20)
            )
            return self.img

    drone1_items = [
        ft.Container(width=200, height=75, content=ft.Text("Launch"), on_click=drone1_launch, bgcolor = ft.colors.GREEN_200, alignment=ft.alignment.center), 
        ft.Container(width=200, height=75, content=ft.Text("Land"), on_click=drone1_land, bgcolor = ft.colors.CYAN_200, alignment=ft.alignment.center),
        ft.Container(width=200, height=75, content=ft.Text("Hover"), on_click=drone1_hover, bgcolor = ft.colors.AMBER, alignment=ft.alignment.center),
    ]

    drone1_column = ft.Column(
        [
            ft.Text(value="Drone #1", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align = ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Column(
                    drone1_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
        ]
    )

    drone2_items = [
        ft.Container( width=200, height=75, content=ft.Text("Launch"), on_click=drone2_launch, bgcolor = ft.colors.GREEN_200, alignment=ft.alignment.center), 
        ft.Container(width=200, height=75, content=ft.Text("Land"), on_click=drone2_land, bgcolor = ft.colors.CYAN_200, alignment=ft.alignment.center),
        ft.Container(width=200, height=75, content=ft.Text("Hover"), on_click=drone2_hover, bgcolor = ft.colors.AMBER, alignment=ft.alignment.center),
    ]

    drone2_column = ft.Column(
        [
            ft.Text(value="Drone #2", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align = ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Column(
                    drone2_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ), 
        ]
    )

    cv2window = ft.Card(
            elevation=30,
            content=ft.Container(
                bgcolor=ft.colors.WHITE24,
                padding=10,
                border_radius = ft.border_radius.all(20),
                content=ft.Column([
                    Countdown(),
                    ft.Text("OPENCV WITH FLET",
                         size=20, weight="bold",
                         color=ft.colors.WHITE),
                ]
                ),
            )
    )

    page.add(
        ft.Row(
            [
                drone1_column,
                drone2_column,
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        ),

        ft.Row(
            controls=[
            ft.Container(width=415, height=75, content=ft.Text("ORDER 66"), on_click=order66, bgcolor = ft.colors.RED, alignment=ft.alignment.center)]
        )
    )

ft.app(target=main)