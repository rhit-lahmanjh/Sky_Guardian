import flet as ft
import time
import threading
import socket
from device_info_reader import read_device_data,edit_device_data


def main(page: ft.Page):

    page.title = "Drone Connection Page"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    device_data = read_device_data()

    # Can only press one connect button at a time
    def droneOneConnect_button(e):

        print("Connecting to Drone 1")
        # User input should be the string or char input to the tello address
        userIPaddress1 = str(input1.value)
        device_data.update({'DRONE1_IP':input1.value})
        
        portValue = 8889

        # print("Address assigned")
        # tello_address = (userIPaddress1, portValue)
        # # Create a UDP connection that we'll send the command to
        # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # local_address = ('192.168.0.234', 9010)
        # print("Sock Binded")
        # # Let's be explicit and bind to a local port on our machine where Tello can send messages
        # sock.bind(local_address)

        # def send(message):
        #     try:
        #         sock.sendto(message.encode(), tello_address)
        #         print("Sending message: " + message)
        #     except Exception as e:
        #         print("Error sending: " + str(e))

        # # Function that listens for messages from Tello and prints them to the screen
        # def receive():
        #     while True:
        #         try:
        #             response1, ip_address = sock.recvfrom(128)
        #             print("Received message from Tello One: " + response1.decode(encoding='utf-8'))
        #         except Exception as e:
        #             sock.close()
        #             print("Error receiving: " + str(e))
        #             break

        # print("daemon Thread")
        # receiveThread = threading.Thread(target=receive)
        # receiveThread.daemon = True
        # receiveThread.start()

        # # Send Tello into command mode
        # # Need to write to a text file and then read IP address from there in the myTello file
        # print("Send Function")
        # send("command")
        # # Receive response from Tello
        # print("Receive Function")
        # receive()
        # # Delay 3 seconds before we send the next command
        # print("Sleep")
        # time.sleep(3)
        # # Ask Tello about battery status
        # print("Battery Status")
        # send("battery?")
        # # Receive battery response from Tello
        # print("Awaiting Reception")
        # receive()
        # print("Response Received")

        # print("Successfully Connected to Drone")
        # print("Closing socket")
        # sock.close()
        # SuccessfulConnection = True
        # if SuccessfulConnection:
        #     page.add("Drone 1 Connection Successful")
        #     page.add(droneContinueButtonRow)
        page.update()

    def droneTwoConnect_button(e):

        print("Connecting to Drone 2")
        # Input appropriate FSM drone logic
        # User input should be the string IP address
        userIPaddress2 = str(input2.value)
        device_data.update({'DRONE2_IP':input2.value})
        # portValue = 8889

        # print("Address assigned")
        # tello2_address = (userIPaddress2, portValue)
        # # Create a UDP connection that we'll send the command to
        # sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # local_address = ('192.168.0.234', 9010)

        # # Let's be explicit and bind to a local port on our machine where Tello can send messages
        # print("Sock Binded")
        # sock2.bind(local_address)

        # def send(message):
        #     try:
        #         sock2.sendto(message.encode(), tello2_address)
        #         print("Sending message: " + message)
        #     except Exception as e:
        #         print("Error sending: " + str(e))

        # # Function that listens for messages from Tello and prints them to the screen
        # def receive():
        #     while True:
        #         try:
        #             response2, ip_address = sock2.recvfrom(128)
        #             print("Received message from Tello Two: " + response2.decode(encoding='utf-8'))
        #         except Exception as e:
        #             sock2.close()
        #             print("Error receiving: " + str(e))
        #             break

        # print("daemon Thread")
        # receiveThread = threading.Thread(target=receive)
        # receiveThread.daemon = True
        # receiveThread.start()

        # # Send Tello into command mode
        # print("Send Function")
        # send("command")
        # # Receive response from Tello
        # print("Receive Function")
        # receive()
        # # Delay 3 seconds before we send the next command
        # print("Sleep")
        # time.sleep(3)
        # # Ask Tello about battery status
        # print("Battery Status")
        # send("battery?")
        # # Receive battery response from Tello
        # print("Awaiting Reception")
        # receive()
        # print("Response Received")

        # print("Successfully Connected to Drone")
        # print("Closing socket")
        # sock2.close()
        # SuccessfulConnection = True
        # if SuccessfulConnection:
        #     page.add("Drone 2 Connection Successful")
        #     page.add(droneContinueButtonRow)
        # print("Successfully Connected to Drone")
        # print("Closing socket")
        # sock2.close()
        # SuccessfulConnection = True
        # if SuccessfulConnection:
        #     page.add("Drone 2 Connection Successful")
        # page.update()


    def window_event(e):
        if e.data == "close":
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()

    page.window_prevent_close = True
    page.on_window_event = window_event

    def yes_click(e):
        edit_device_data(device_data)
        page.window_destroy()

    def no_click(e):
        confirm_dialog.open = False
        page.update()

    def continueButton(e):
        print("Routing to Dashboard")

    input1 = ft.TextField(label="Enter New IP Address", on_submit=droneOneConnect_button)

    droneOneConnectionItems = [
        # Want to use input from text field
        input1,
        ft.ElevatedButton(text="Save",color=ft.colors.BLACK,on_click=droneOneConnect_button, bgcolor=ft.colors.AMBER),
    ]

    droneOneConnectionRow = ft.Row(
        [
            ft.Text(value="Drone 1", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Row(
                    droneOneConnectionItems,
                    alignment=ft.MainAxisAlignment.CENTER),
            )
        ]
    )

    input2 = ft.TextField(label="Enter New IP Address", on_submit=droneTwoConnect_button)

    droneTwoConnectionItems = [
        # Want to use input from text field
        input2,
        ft.ElevatedButton(text="Save",color=ft.colors.BLACK, on_click=droneTwoConnect_button, bgcolor=ft.colors.AMBER)
    ]

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

    droneContinueButtonItems = [
        ft.ElevatedButton(text="Continue",color=ft.colors.BLACK, on_click=continueButton, bgcolor=ft.colors.GREEN_200)
    ]

    droneContinueButtonRow = ft.Row(
        [
            ft.Container(
                content=ft.Row(
                    droneContinueButtonItems,
                    alignment=ft.MainAxisAlignment.END),
            )
        ]
    )

    page.add(
    ft.Column(
        [
            droneOneConnectionRow,
            droneTwoConnectionRow,
            droneContinueButtonRow
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

    dr1 = ft.Text(value=f"Current Drone 1 Router IP: {device_data.get('DRONE1_IP')}", color="white",scale=1,weight=4)
    page.controls.append(dr1)
    dr2 = ft.Text(value=f"Current Drone 2 Router IP: {device_data.get('DRONE2_IP')}", color="white",scale=1,weight=4)
    page.controls.append(dr2)
    # ds = ft.Text(value="Drone Single IP: 192.168.10.1", color="black")
    # page.controls.append(ds)
    page.update()

ft.app(target=main)