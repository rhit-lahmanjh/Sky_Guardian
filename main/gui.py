#!/bin/env python
from drone import (Drone, State)
import flet as ft
import djitellopy
import socket
import time
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

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind(local_address)

# def send(message, delay):
#     try:
#         sock.sendto(message.encode(), tello_address)
#         print("Sending message: " + message)
#     except Exception as exp:
#         print("Error sending: " + str(exp))

#     time.sleep(delay)
    
# def recieve():
#     while True:
#         try:
#             response, ip_address = sock.recvfrom(128)
#             print("Recieved message: " + response.decode(encoding='utf-8'))
#         except Exception as exp:
#             sock.close()
#             print("Error recieving: " + str(exp))
#             break
        
def main(page: ft.Page):
    # drone connection
    drone1 = Drone('test')
    # time.sleep(5)
    threads = []
    FSM_thread = threading.Thread(target=drone1.operate)
    threads.append(FSM_thread)
    FSM_thread.start()

    page.title = "Drone Basic Functions"
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Button functions
    def drone1_launch(e):
        print("Drone 1 State: Takeoff")
        # send("command", 3)
        # send("takeoff", 5)

        drone1.opState = State.Takeoff
        # drone1.operate()
        # t1 = threading.Thread(target=drone1.operate)
        # threads.append(t1)
        page.update()
    
    def drone2_launch(e):
        print("Drone 2 State: Takeoff")
        # drone2.opState = State.Takeoff
        page.update()

    def drone1_land(e):
        print("Drone 1 State: Landed")
        # send("land", 5)
        # drone1.land()
        drone1.opState = State.Landed
        page.update()
    
    def drone2_land(e):
        print("Drone 2 State: Landed")           
    #     drone2.opState = State.Landed
        page.update()

    def drone1_hover(e):
        print("Drone 1 State: Hover")  
        # send("hover", 3)         
        drone1.opState = State.Hover
        # h1 = threading.Thread(target=drone1.operate)
        # threads.append(h1)
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
        drone2.opState = State.Hover
        page.update()        

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
    # FSM_thread.start()

ft.app(target=main)