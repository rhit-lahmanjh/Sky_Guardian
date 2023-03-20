import flet as ft
import djitellopy
import socket
import time
import threading
#from drone import (Drone, State)

# tello_address = ('192.168.10.1', 8889)
# local_address = ('', 9000)

# Incorporate Function to send messages to the Tello drone
# myTello.py lines 21 - 27

# Incorporate Function that listens for messages from Tello and prints them to the screen
# myTello.py lines 30 - 41

def main(page: ft.Page):

    page.title = "Drone Connection Page"
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def droneOneConnect_button(e):

        print("Connecting to Drone 1")
        # User input should be the string input
        tello_address = ('192.168.0.248', 8889)
        # Input appropriate FSM drone logic
        # Create a UDP connection that we'll send the command to tello drone
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Let's be explicit and bind to a local port on our machine where Tello can send messages
        sock.bind(('', 9000))

        # Send Tello into command mode
        #send("command")
        # Receive response from Tello
        #receive()
        # Delay 3 seconds before we send the next command
        #time.sleep(3)
        # Ask Tello about battery status
        #send("battery?")
        # Receive battery response from Tello
        #receive()

        # input lines 43 - 45

        page.update()

    def droneTwoConnect_button(e):

        print("Connecting to Drone 2")
        # Input appropriate FSM drone logic
        # User input should be the string IP address
        tello2_address = ('192.168.0.140', 8889)
        # Create a UDP connection that we'll send the command to tello drone
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Let's be explicit and bind to a local port on our machine where Tello can send
        sock2.bind(('', 9010))
        # Send Tello into command mode
        # send("command")
        # Receive response from Tello
        # receive()
        # Delay 3 seconds before we send the next command
        # time.sleep(3)
        # Ask Tello about battery status
        # send("battery?")
        # Receive battery response from Tello
        # receive()

        # input lines 43 - 45

        ## if the messages can be sent and recieved, set a boolean flag to true
        ## Create a continue button function, and then place its function call within a conditional statement
        ## boolean flag for both drones has to be true
        ## Make continue button green color to indicate affirmative action to proceed

        page.update()

    def window_event(e):
        if e.data == "close":
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()

    page.window_prevent_close = True
    page.on_window_event = window_event

    def yes_click(e):
        # close the UDP sockets
        #sock.close()
        #sock2.close()
        page.window_destroy()

    def no_click(e):
        confirm_dialog.open = False
        page.update()

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