import flet as ft
import time
import threading
import socket
import pickle
import csv

# tello_address = ('192.168.10.1', 8889)
# local_address = ('', 9000)
def main(page: ft.Page):

    # tello_address = ('192.168.10.1', 8889)
    # local_address = ('', 9000)
    page.title = "Drone Connection Page"
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Can only press one connect button at a time
    def droneOneConnect_button(e):

        print("Connecting to Drone 1")
        # User input should be the string or char input to the tello address
        userIPaddress1 = str(input1.value)
        portValue = 8889

        # csv code for writing to csv file
        # values = [userIPaddress1, portValue]
        # with open('Drone1.csv', 'w') as file:
        #     writer = csv.writer(file)
        #     writer.writerow(values)

        # Pickle Code for writing to txt file
        # with open("ip_fileDrone1.txt", "wb") as file_handler:
        #     pickle.dump((userIPaddress1, portValue), (file_handler))
        # input()

        tello_address = (userIPaddress1, portValue)
        # Create a UDP connection that we'll send the command to
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Let's be explicit and bind to a local port on our machine where Tello can send messages
        sock.bind(('', 9000))
        def send(message):
            try:
                sock.sendto(message.encode(), tello_address)
                print("Sending message: " + message)
            except Exception as e:
                print("Error sending: " + str(e))

        # Function that listens for messages from Tello and prints them to the screen
        def receive():
            while True:
                try:
                    response1, ip_address = sock.recvfrom(128)
                    print("Received message from Tello One: " + response1.decode(encoding='utf-8'))
                except Exception as e:
                    sock.close()
                    print("Error receiving: " + str(e))
                    break

        receiveThread = threading.Thread(target=receive)
        receiveThread.daemon = True
        receiveThread.start()

        # Send Tello into command mode
        # Need to write to a text file and then read IP address from there in the myTello file
        send("command")
        # Receive response from Tello
        receive()
        # Delay 3 seconds before we send the next command
        time.sleep(3)
        # Ask Tello about battery status
        send("battery?")
        # Receive battery response from Tello
        receive()

        print("Successfully Connected to Drone")
        sock.close()
        SuccessfulConnection = True
        if SuccessfulConnection:
            page.add("Drone 1 Connection Successful")
            page.add(droneContinueButtonRow)
        page.update()

    def droneTwoConnect_button(e):

        print("Connecting to Drone 2")
        # Input appropriate FSM drone logic
        # User input should be the string IP address
        userIPaddress2 = str(input2.value)
        portValue = 8889

        # # csv code for writing to csv file
        # values = [userIPaddress2, portValue]
        # with open('Drone2.csv', 'w') as file:
        #     writer = csv.writer(file)
        #     writer.writerow(values)

        # Pickle Code for writing to txt file
        # with open("ip_fileDrone2.txt", "wb") as file_handler:
        #     pickle.dump((userIPaddress2, portValue), (file_handler))
        # input()

        tello2_address = (userIPaddress2, portValue)
        # Create a UDP connection that we'll send the command to
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Let's be explicit and bind to a local port on our machine where Tello can send messages
        sock2.bind(('', 9010))

        def send(message):
            try:
                sock2.sendto(message.encode(), tello2_address)
                print("Sending message: " + message)
            except Exception as e:
                print("Error sending: " + str(e))

        # Function that listens for messages from Tello and prints them to the screen
        def receive():
            while True:
                try:
                    response2, ip_address = sock2.recvfrom(128)
                    print("Received message from Tello Two: " + response2.decode(encoding='utf-8'))
                except Exception as e:
                    sock2.close()
                    print("Error receiving: " + str(e))
                    break

        receiveThread = threading.Thread(target=receive)
        receiveThread.daemon = True
        receiveThread.start()

        # Send Tello into command mode
        send("command")
        # Receive response from Tello
        receive()
        # Delay 3 seconds before we send the next command
        time.sleep(3)
        # Ask Tello about battery status
        send("battery?")
        # Receive battery response from Tello
        receive()

        print("Successfully Connected to Drone")
        sock2.close()
        SuccessfulConnection = True
        if SuccessfulConnection:
            page.add("Drone 2 Connection Successful")
            page.add(droneContinueButtonRow)

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

    def continueButton(e):
      print("Routing to Dashbord")

    input1 = ft.TextField(label="Enter IP Address, i.e. 192.168.0.248", on_submit=droneOneConnect_button)

    droneOneConnectionItems = [
        # Want to use input from text field
        input1,
        ft.ElevatedButton(text="Connect", on_click=droneOneConnect_button, bgcolor=ft.colors.AMBER),
    ]

    input2 = ft.TextField(label="Enter IP Address, i.e. 192.168.0.140", on_submit=droneTwoConnect_button)

    droneTwoConnectionItems = [
        # Want to use input from text field
        input2,
        ft.ElevatedButton(text="Connect", on_click=droneTwoConnect_button, bgcolor=ft.colors.AMBER)
    ]

    droneContinueButtonItems = [
        ft.ElevatedButton(text="Continue", on_click=continueButton, bgcolor=ft.colors.GREEN_200)
    ]

    droneOneConnectionRow = ft.Row(
        [
            ft.Text(value="Drone 1", style=ft.TextThemeStyle.DISPLAY_SMALL,text_align=ft.TextAlign.CENTER),
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