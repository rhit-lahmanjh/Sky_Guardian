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

        page.update()

    def droneTwoConnect_button(e):

        print("Connecting to Drone 2")
        # User input should be the string IP address
        userIPaddress2 = str(input2.value)
        device_data.update({'DRONE2_IP':input2.value})

        page.update()

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

    input2 = ft.TextField(label="Enter New IP Address", on_submit=droneTwoConnect_button)

    droneTwoConnectionItems = [
        # Want to use input from text field
        input2,
        ft.ElevatedButton(text="Save",color=ft.colors.BLACK, on_click=droneTwoConnect_button, bgcolor=ft.colors.AMBER)
    ]

    droneContinueButtonItems = [
        ft.ElevatedButton(text="Continue",color=ft.colors.BLACK, on_click=continueButton, bgcolor=ft.colors.GREEN_200)
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

# csv code for writing to csv file
# values = [userIPaddress1, portValue]
# with open('Drone1.csv', 'w') as file:
#     writer = csv.writer(file)
#     writer.writerow(values)

# Pickle Code for writing to txt file
# with open("ip_fileDrone1.txt", "wb") as file_handler:
#     pickle.dump((userIPaddress1, portValue), (file_handler))
# input()

# # csv code for writing to csv file
# values = [userIPaddress2, portValue]
# with open('Drone2.csv', 'w') as file:
#     writer = csv.writer(file)
#     writer.writerow(values)

# Pickle Code for writing to txt file
# with open("ip_fileDrone2.txt", "wb") as file_handler:
#     pickle.dump((userIPaddress2, portValue), (file_handler))
# input()

# # csv code for writing to csv file
# values = [userIPaddress2, portValue]
# with open('Drone2.csv', 'w') as file:
#     writer = csv.writer(file)
#     writer.writerow(values)

# Pickle Code for writing to txt file
# with open("ip_fileDrone2.txt", "wb") as file_handler:
#     pickle.dump((userIPaddress2, portValue), (file_handler))
# input()