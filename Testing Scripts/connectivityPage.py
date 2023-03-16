import flet as ft
import djitellopy
import socket
import time
import threading
#from drone import (Drone, State)

# tello_address = ('192.168.10.1', 8889)
# local_address = ('', 9000)

# This is updated Connectivity page after the Onnx Github implosion
def main(page: ft.Page):

    page.title = "Drone Connection Page"
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # def connect_button(e):
    #     if not t.value:
    #         t.error_text = "IP Address Format: 192.168.10.1"
    #         page.update()
    #     else:
    #         t.value = f"Textboxes values are: '{tb1.value}', '{tb2.value}'."
    #         page.update()
    #         page.add(ft.Text(tb1.value))
    #         # Connect to drone

    def droneOneConnect_button(e):
        print("Connecting to Drone 1")
        # Input appropriate FSM drone logic

        page.update()

    def droneTwoConnect_button(e):
        print("Connecting to Drone 2")
        # Input appropriate FSM drone logic
        page.update()

    def window_event(e):
        if e.data == "close":
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()

    page.window_prevent_close = True
    page.on_window_event = window_event

    def yes_click(e):
        page.window_destroy()

    def no_click(e):
        confirm_dialog.open = False
        page.update()


    # # Expand to automatically add IP address fields as the number of drones present is selected from UI
    # t = ft.Text()
    # tb1 = ft.TextField(label="Enter Drone 1 IP Address")
    # b1 = ft.ElevatedButton(text="Connect to Drone", on_click=connect_button)
    # tb2 = ft.TextField(label="Enter Drone 2 IP Address")
    # b2 = ft.ElevatedButton("Connect to Drone", on_click=connect_button)
    # page.add(tb1, b1, tb2, b2)


    droneOneConnectionItems = [
        ft.TextField(label="Enter Drone 1 IP Address"),
        ft.ElevatedButton(text="Connect to Drone", on_click=droneOneConnect_button)
    ]

    droneTwoConnectionItems = [
        ft.TextField(label="Enter Drone 2 IP Address", ),
        ft.ElevatedButton(text="Connect to Drone", on_click=droneTwoConnect_button)
    ]

    droneOneConnectionRow = ft.Row(
        [
            ft.Text(value="Drone 1", style=ft.TextThemeStyle.DISPLAY_SMALL),
            ft.Container(
                content=ft.Row(
                    droneOneConnectionItems,
                    alignment=ft.MainAxisAlignment.CENTER),
                )

        ]
    )

    droneTwoConnectionRow = ft.Row(
        [
        ft.Text(value="Drone 2", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align=ft.TextAlign.CENTER),
        ft.Container(
            content=ft.Row(
                droneTwoConnectionItems,
                alignment=ft.MainAxisAlignment.CENTER),
                )
        ]
    )

    page.add(
    ft.Column(
        [
            droneOneConnectionRow,
            droneTwoConnectionRow,
        ],
        spacing=50,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    )

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please Confirm"),
        content=ft.Text("Do you wish to exit the app?"),
        actions=[
            ft.ElevatedButton("Yes", on_click=yes_click),
            ft.OutlinedButton("No", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )



    page.add(ft.Text('Try exiting this app by clicking window "Close" button'))

ft.app(target=main)