#!/bin/env python
# import drone
import flet as ft
# import djitellopy
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


def main(page: ft.Page):
    # # drone connection
    # tello = Tello()
    # tello.connect()

    # drone1 = Drone('test')
    # drone1.operate()

    page.title = "Drone Basic Functions"
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Button functions
    def drone1_launch(e):
        print("Drone 1 State: Takeoff")
    #     drone1.opState = State.Takeoff
        page.update()
    
    def drone2_launch(e):
        print("Drone 2 State: Takeoff")
    #     drone2.opState = State.Takeoff
        page.update()

    def drone1_land(e):
        print("Drone 1 State: Landed")
    #     drone1.opState = State.Landed
        page.update(e)
    
    def drone2_land(e):
        print("Drone 2 State: Landed")           
    #     drone2.opState = State.Landed
        page.update()

    def drone1_hover(e):
        print("Drone 1 State: Hover")           
        #     drone1.opState = State.Hover
        page.update()
    
    def drone2_hover(e):
        print("Drone 2 State: Hover")           
        #     drone2.opState = State.Hover
        page.update()
    
    def order66(e):
        print("Drone 1 State: Landed")
        print("Drone 2 State: Landed")

        #     drone1.opState = State.Landed
        #     drone2.opState = State.Landed
        page.update()        

    drone1_items = [
        ft.Container( width=200, height=75, content=ft.Text("Launch"), on_click=drone1_launch, bgcolor = ft.colors.GREEN_200, alignment=ft.alignment.center), 
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
            spacing=30,
            alignment=ft.MainAxisAlignment.START,
        )
    )

ft.app(target=main)