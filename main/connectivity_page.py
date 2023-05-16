import flet as ft
from device_info_reader import read_device_data,edit_device_data


def main(page: ft.Page):

    page.title = "Drone Connection Properties Page"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    device_data = read_device_data()

    def droneOneIPSaveButton(e):

        print("Storing Drone 1 IP Address")
        device_data.update({'DRONE1_IP':input1.value})

    def droneTwoIPSaveButton(e):

        print("Storing Drone 2 IP Address")
        device_data.update({'DRONE2_IP':input2.value})

    def ssidSaveButton(e):
        print("Storing Router SSID")

    def passwordSaveButton(e):
        print("Storing Router Password")


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

    input1 = ft.TextField(label="Enter New IP Address", on_submit=droneOneIPSaveButton)

    droneOneConnectionItems = [
        # Want to use input from text field
        input1,
        ft.ElevatedButton(text="Save", color=ft.colors.BLACK, on_click=droneOneIPSaveButton, bgcolor=ft.colors.AMBER),
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

    input2 = ft.TextField(label="Enter New IP Address", on_submit=droneTwoIPSaveButton)

    droneTwoConnectionItems = [
        # Want to use input from text field
        input2,
        ft.ElevatedButton(text="Save", color=ft.colors.BLACK, on_click=droneTwoIPSaveButton, bgcolor=ft.colors.AMBER)
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
    dr1 = ft.Text(value=f"Current Drone 1 Router IP: {device_data.get('DRONE1_IP')}", color="white", scale=1, weight=4)
    page.controls.append(dr1)
    page.update()
    dr2 = ft.Text(value=f"Current Drone 2 Router IP: {device_data.get('DRONE2_IP')}", color="white", scale=1, weight=4)
    page.controls.append(dr2)
    page.update()

ft.app(target=main)