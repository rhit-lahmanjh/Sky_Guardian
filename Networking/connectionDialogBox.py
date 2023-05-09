import flet as ft
import time
import threading
import socket

def main(page: ft.Page):
    page.title = "Drone Connection Dialog"

    # Formatting
    # Storing values

    def droneOneConnect_button(e):

        print("Connecting to Drone 1")
        # User input should be the string or char input to the tello address
        userIPaddress1 = str(input1.value)
        portValue = 8889

        print("Address assigned")
        tello_address = (userIPaddress1, portValue)
        # Create a UDP connection that we'll send the command to
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_address = ('192.168.0.234', 9010)
        print("Sock Binded")
        # Let's be explicit and bind to a local port on our machine where Tello can send messages
        sock.bind(local_address)

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

        print("daemon Thread")
        receiveThread = threading.Thread(target=receive)
        receiveThread.daemon = True
        receiveThread.start()

        # Send Tello into command mode
        # Need to write to a text file and then read IP address from there in the myTello file
        print("Send Function")
        send("command")
        # Receive response from Tello
        print("Receive Function")
        receive()
        # Delay 3 seconds before we send the next command
        print("Sleep")
        time.sleep(3)
        # Ask Tello about battery status
        print("Battery Status")
        send("battery?")
        # Receive battery response from Tello
        print("Awaiting Reception")
        receive()
        print("Response Received")

        print("Successfully Connected to Drone")
        print("Closing socket")
        sock.close()
        SuccessfulConnection = True
        SuccessfulConnection = True
        if SuccessfulConnection:
            print("Ready to Continue?")

    def droneTwoConnect_button(e):

        print("Connecting to Drone 2")
        # Input appropriate FSM drone logic
        # User input should be the string IP address
        userIPaddress2 = str(input2.value)
        portValue = 8889

        print("Address assigned")
        tello2_address = (userIPaddress2, portValue)
        # Create a UDP connection that we'll send the command to
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_address = ('192.168.0.234', 9010)

        # Let's be explicit and bind to a local port on our machine where Tello can send messages
        print("Sock Binded")
        sock2.bind(local_address)

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

        print("daemon Thread")
        receiveThread = threading.Thread(target=receive)
        receiveThread.daemon = True
        receiveThread.start()

        # Send Tello into command mode
        print("Send Function")
        send("command")
        # Receive response from Tello
        print("Receive Function")
        receive()
        # Delay 3 seconds before we send the next command
        print("Sleep")
        time.sleep(3)
        # Ask Tello about battery status
        print("Battery Status")
        send("battery?")
        # Receive battery response from Tello
        print("Awaiting Reception")
        receive()
        print("Response Received")

        print("Successfully Connected to Drone")
        print("Closing socket")
        sock2.close()
        SuccessfulConnection = True
        if SuccessfulConnection:
            print("Ready to Continue?")


    def close_dlg(e):
        dlg_modal.open = False
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

    def open_dlg(e):
        page.dialog = dlg
        dlg.open = True
        page.update()

    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    page.add(
        ft.ElevatedButton("IP Addresses", on_click=open_dlg),
        ft.ElevatedButton("Connection Testing", on_click=open_dlg_modal),
    )

    dlg = ft.AlertDialog(
        title=ft.Text("Drone IP Addresses"),
        content=ft.Text("Drone 1 Router IP: 192.168.0.248, "
                        "Drone 2 Router IP: 192.168.0.140, "
                        "Drone Single IP: 192.168.10.1"),
        on_dismiss=lambda e: print("Dialog dismissed!")
    )

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Connection Testing"),
        content=ft.Text("Input Drone IP Addresses"),
        actions=[
            #ft.TextField(label="Drone 1 IP Address"),
            #ft.TextField(label="Drone 2 IP Address"),
            ft.TextField(label="Drone 1 IP Address",on_submit=droneOneConnect_button),
            ft.TextField(label="Drone 2 IP Address",on_submit=droneTwoConnect_button),
            ft.ElevatedButton("Connect Drone 1", on_click=close_dlg, bgcolor=ft.colors.BLUE_400),
            ft.ElevatedButton("Connect Drone 2", on_click=close_dlg, bgcolor=ft.colors.AMBER),
            ft.ElevatedButton("Continue", on_click=close_dlg, bgcolor=ft.colors.GREEN_200),
            ft.ElevatedButton("Close", on_click=close_dlg, bgcolor=ft.colors.RED_400),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
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