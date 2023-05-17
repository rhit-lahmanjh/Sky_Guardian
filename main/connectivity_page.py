import flet as ft
from device_info_reader import read_device_data,edit_device_data


def main(page: ft.Page):

    page.title = "Drone Connection Properties Page"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    device_data = read_device_data()

    def droneOneIPSaveButton(e):
        if droneOneIPInput != "":
            print("Storing Drone 1 IP Address")
            device_data.update({'DRONE1_IP':droneOneIPInput.value})
            droneOneCurrentIPDisplay.value = f"Current Drone 1 Router IP: {device_data.get('DRONE1_IP')}"
            droneOneCurrentIPDisplay.update()
        else:
            print("No Input")

    def droneTwoIPSaveButton(e):
        if droneTwoIPInput != "":
            print("Storing Drone 2 IP Address")
            device_data.update({'DRONE2_IP':droneTwoIPInput.value})
            droneTwoCurrentIPDisplay.value = f"Current Drone 2 Router IP: {device_data.get('DRONE2_IP')}"
            droneTwoCurrentIPDisplay.update()
        else:
            print("No Input")

    def ssidSaveButton(e):
        if ssidInput != "":
            print("Storing Router SSID")
            device_data.update({'ROUTER_SSID':ssidInput.value})
            currentRouterSSIDDisplay.value = f"Current Router SSID: {device_data.get('DRONE1_IP')}"
            currentRouterSSIDDisplay.update()
        else:
            print("No Input")

    def passwordSaveButton(e):
        if routerPasswordInput.value != "":
            print(f"Storing Router Password as: {routerPasswordInput.value}")
            device_data.update({'ROUTER_PASSWORD':routerPasswordInput.value})
            page.update()
        else:
            print("No Input")

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

    droneOneIPInput = ft.TextField(label="Enter New IP Address", on_submit=droneOneIPSaveButton)

    droneOneConnectionItems = [
        # Want to use input from text field
        droneOneIPInput,
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

    droneTwoIPInput = ft.TextField(label="Enter New IP Address", on_submit=droneTwoIPSaveButton)

    droneTwoConnectionItems = [
        # Want to use input from text field
        droneTwoIPInput,
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

    ssidInput = ft.TextField(label="Enter SSID", on_submit=ssidSaveButton)

    ssidConnectionItems = [
        # using input from SSID text field
        ssidInput,
        ft.ElevatedButton(text="Save",color=ft.colors.BLACK, on_click=ssidSaveButton, bgcolor=ft.colors.AMBER)
    ]

    ssidConnectionRow = ft.Row(
        [
            ft.Text(value="Router SSID", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Row(
                    ssidConnectionItems,
                    alignment=ft.MainAxisAlignment.CENTER),
            )
        ]
    )

    routerPasswordInput = ft.TextField(label="Enter Password", on_submit=passwordSaveButton)

    routerPasswordConnectionItems = [
        # using input from router password text field
        routerPasswordInput,
        ft.ElevatedButton(text="Save", color=ft.colors.BLACK, on_click=passwordSaveButton, bgcolor=ft.colors.AMBER)
    ]

    routerPasswordConnectionRow = ft.Row(
        [
            ft.Text(value="Router Password", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align=ft.TextAlign.CENTER),
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
        content=ft.Text("Do you wish to exit the page?"),
        actions=[
            ft.ElevatedButton("Yes", on_click=yes_click),
            ft.OutlinedButton("No", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    droneOneCurrentIPDisplay = ft.Text(value=f"Current Drone 1 Router IP: {device_data.get('DRONE1_IP')}", color="white", scale=1, weight=4)
    page.controls.append(droneOneCurrentIPDisplay)
    droneTwoCurrentIPDisplay = ft.Text(value=f"Current Drone 2 Router IP: {device_data.get('DRONE2_IP')}", color="white", scale=1, weight=4)
    page.controls.append(droneTwoCurrentIPDisplay)
    currentRouterSSIDDisplay = ft.Text(value=f"Current Router SSID: {device_data.get('ROUTER_SSID')}", color="white", scale=1, weight=4)
    page.controls.append(currentRouterSSIDDisplay)
    routerPasswordDisplay = ft.Text(value="Router Password Printed to Terminal",color="white", scale=1, weight=4)
    page.update()

    # Password printed to terminal, for security against OSINT/Public Knowledge password is not displayed on page
    print(f"Current Router Password: {device_data.get('ROUTER_PASSWORD')}")

ft.app(target=main)