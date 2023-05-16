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

        print("Storing Drone 2 IP Address")
        device_data.update({'DRONE2_IP':input2.value})


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

    ssidInput = ft.TextField(label="Enter Router SSID Name", on_submit=ssidSaveButton)

    ssidConnectionItems = [
        # using input from SSID text field
        ssidInput,
        ft.ElevatedButton(text="Save",color=ft.colors.BLACK, on_click=ssidSaveButton, bgcolor=ft.colors.AMBER)
    ]

    ssidConnectionRow = ft.Row(
        [
            ft.Text(value="SSID", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Row(
                    ssidConnectionItems,
                    alignment=ft.MainAxisAlignment.CENTER),
            )
        ]
    )

    routerPasswordInput = ft.TextField(label="Enter Router Password", on_submit=passwordSaveButton)

    routerPasswordConnectionItems = [
        # using input from router password text field
        routerPasswordInput,
        ft.ElevatedButton(text="Save", color=ft.colors.BLACK, on_click=passwordSaveButton, bgcolor=ft.colors.AMBER)
    ]

    routerPasswordConnectionRow = ft.Row(
        [
            ft.Text(value="Password", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Row(
                    routerPasswordConnectionItems,
                    alignment=ft.MainAxisAlignment.CENTER),
            )
        ]
    )

    page.add(
    ft.Column(
        [
            droneOneConnectionRow,
            droneTwoConnectionRow,
            ssidConnectionRow,
            routerPasswordConnectionRow
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

    page.update()
    dr1 = ft.Text(value=f"Current Drone 1 Router IP: {device_data.get('DRONE1_IP')}", color="white",scale=1,weight=4)
    page.controls.append(dr1)
    page.update()
    dr2 = ft.Text(value=f"Current Drone 2 Router IP: {device_data.get('DRONE2_IP')}", color="white",scale=1,weight=4)
    page.controls.append(dr2)
    page.update()

ft.app(target=main)