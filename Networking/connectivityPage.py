import flet as ft
import socket
import time
import threading
import myTello

# tello_address = ('192.168.10.1', 8889)
# local_address = ('', 9000)

def main(page: ft.Page):

    page.title = "Drone Connection Page"
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Can only press one connect button at a time
    def droneOneConnect_button(e):

        print("Connecting to Drone 1")
        # User input should be the string or char input to the tello address
        userIPaddress = str(input1.value)

        receiveThread = threading.Thread(target=myTello.receive)
        receiveThread.daemon = True
        receiveThread.start()

        # Send Tello into command mode
        # Need to write to a text file and then read IP address from there in the myTello file
        myTello.send("command", (userIPaddress, 8889))
        # Receive response from Tello
        myTello.receive()
        # Delay 3 seconds before we send the next command
        time.sleep(3)
        # Ask Tello about battery status
        myTello.send("battery?", (userIPaddress, 8889))
        # Receive battery response from Tello
        myTello.receive()

        print("Successfully Connected to Drone")
        myTello.sock.close()
        SuccessfulConnection = True
        if SuccessfulConnection:
            page.add("Drone 1 Connection Successful")
            page.add(droneContinueButtonRow)

        page.update()

    def droneTwoConnect_button(e):

        print("Connecting to Drone 2")
        # Input appropriate FSM drone logic
        # User input should be the string IP address
        userIPaddress = str(input2.value)

        receiveThread = threading.Thread(target=myTello.receive)
        receiveThread.daemon = True
        receiveThread.start()

        # Send Tello into command mode
        myTello.send("command", (userIPaddress, 8889))
        # Receive response from Tello
        myTello.receive()
        # Delay 3 seconds before we send the next command
        time.sleep(3)
        # Ask Tello about battery status
        myTello.send("battery?", (userIPaddress, 8889))
        # Receive battery response from Tello
        myTello.receive()

        print("Successfully Connected to Drone")
        myTello.sock2.close()
        SuccessfulConnection = True
        if SuccessfulConnection:
            page.add("Drone 2 Connection Successful")
            page.add(droneContinueButtonRow)

        page.update()

    ## if the messages can be sent and recieved, set a boolean flag to true
    ## Create a continue button function, and then place its function call within a conditional statement
    ## boolean flag for both drones has to be true
    ## Make continue button green color to indicate affirmative action to proceed

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

    def continueButton(e):
      print("Routing to Dashbord")

    input1 = ft.TextField(label="Enter Drone 1 IP Address", on_submit=droneOneConnect_button)

    droneOneConnectionItems = [
        # Want to use input from text field
        input1,
        ft.ElevatedButton(text="Connect", on_click=droneOneConnect_button, bgcolor = ft.colors.AMBER)
    ]

    input2 = ft.TextField(label="Enter Drone 2 IP Address", on_submit=droneTwoConnect_button)

    droneTwoConnectionItems = [
        # Want to use input from text field
        input2,
        ft.ElevatedButton(text="Connect", on_click=droneTwoConnect_button, bgcolor = ft.colors.AMBER)
    ]

    droneContinueButtonItems = [
        ft.ElevatedButton(text="Continue", on_click=continueButton, bgcolor = ft.colors.GREEN_200)
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

    droneContinueButtonRow = ft.Row(
        [
            ft.Container(
                content=ft.Row(
                    droneContinueButtonItems,
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

ft.app(target=main)