#!/bin/env python
from drone import (Drone, State)
import flet as ft
import djitellopy
import socket
import time
import numpy as np
import cv2
import base64
import threading
from flet import (
    Column,
    Container,
    ElevatedButton,
    Page,
    Row,
    Text,
    border_radius,
    colors,
    CrossAxisAlignment,
)
from behaviors.behavior import behavior1

# tello_address = ('192.168.10.1', 8889)
# local_address = ('', 9000)
        
def main(page: ft.Page):
    # drone connection
    drone1 = Drone(identifier = 'test',behavior = behavior1)
    cap = drone1.SensoryState.videoCapture

    # Setting up threading
    threads = []
    FSM_thread = threading.Thread(target=drone1.operate)
    threads.append(FSM_thread)
    FSM_thread.start()

    page.title = "Drone Basic Functions"

    # Button functions
    def drone1_launch(e):
        print("Drone 1 State: Takeoff")
        drone1.opState = State.Takeoff
        page.update()
    
    def drone2_launch(e):
        print("Drone 2 State: Takeoff")
        # drone2.opState = State.Takeoff
        page.update()

    def drone1_land(e):
        print("Drone 1 State: Landed")
        drone1.opState = State.Landed
        page.update()
    
    def drone2_land(e):
        print("Drone 2 State: Landed")           
    #     drone2.opState = State.Landed
        page.update()

    def drone1_hover(e):
        print("Drone 1 State: Hover")  
        drone1.opState = State.Hover
        page.update()
    
    def drone2_hover(e):
        print("Drone 2 State: Hover")           
        #     drone2.opState = State.Hover
        page.update()
    
    def order66(e):
        print("Order 66")
        print("Drone 1 State: Hover")           
        print("Drone 2 State: Hover")

        drone1.opState = State.Hover
        # drone2.opState = State.Hover
        page.update()        

    class Countdown(ft.UserControl):
		cv2.namedWindow("Video Stream",cv2.WINDOW_NORMAL)
		cv2.resizeWindow("Video Stream",400,600)

		# # AND SAVE THE FILE NAME WITH TIME NOW 
		# timestamp = str(int(time.time()))
		# myfileface = str("myCumFaceFile" + "_" + timestamp + '.jpg')
		try:
			while True:
				ret,frame = cap.read()
				cv2.imshow("Webcam",frame)
				myimage.src = ""
				page.update()

				# AFTER THAT WAITING YOU INPUT FROM KEYBOARD
				key = cv2.waitKey(1)

				# AND IF YOU PRESS Q FROM YOU KEYBOARD THEN
				# THE WEBCAM WINDOW CAN CLOSE 
				# AND YOU NOT CAPTURE YOU IMAGE
				if key == ord("q"):
					break
				elif key == ord("s"):
					# AND IF YOU PRESS s FROM YOU KEYBOARD
					# THE THE YOU CAPTURE WILL SAVE IN FOLDER YOUPHOTO
					cv2.imwrite(f"youphoto/{myfileface}",frame)
					# AND SHOW TEXT YOU PICTURE SUCCESS INPUT
					cv2.putText(frame,"YOU SUCESS CAPTURE GUYS !!!",(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
					cv2.imshow("Webcam",frame)
					cv2.waitKey(3000)
					folder_path = "youphoto/"
					myimage.src = folder_path + myfileface
					page.update()
					break

			cap.release()
			cv2.destroyAllWindows()
			page.update()

    # CV2 Window 
    class Countdown(ft.UserControl):
        def __init__(self):
            super().__init__()

        def did_mount(self):
            self.update_timer()

        def update_timer(self):
            while True:
                drone1.sensoryState.__clearBuffer__(drone1.sensoryState.videoCapture)
                _, frame = drone1.sensoryState.videoCapture
                # frame = cv2.resize(frame,(400,400))
                _, im_arr = cv2.imencode('.png', frame)
                im_b64 = base64.b64encode(im_arr)
                self.img.src_base64 = im_b64.decode("utf-8")
                self.update()

                # img_b64 = drone1.sensoryState.image
                # print(type(drone1.sensoryState.image))
                # # img_b64 = ndarray_to_b64(np.array(drone1.sensoryState.image).astype('uint8'))
                # self.img = drone1.sensoryState.image
                # self.update()

        def build(self):
            self.img = ft.Image(
                border_radius=ft.border_radius.all(20)
            )
            return self.img

    def ndarray_to_b64(ndarray):
    # converts a np ndarray to a b64 string readable by html-img tags 
        img = cv2.cvtColor(ndarray, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.png', img)
        return base64.b64encode(buffer).decode('utf-8')

    drone1_items = [
        ft.Container(width=200, height=75, content=ft.Text("Launch"), on_click=drone1_launch, bgcolor = ft.colors.GREEN_200, alignment=ft.alignment.center), 
        ft.Container(width=200, height=75, content=ft.Text("Land"), on_click=drone1_land, bgcolor = ft.colors.CYAN_200, alignment=ft.alignment.center),
        ft.Container(width=200, height=75, content=ft.Text("Hover"), on_click=drone1_hover, bgcolor = ft.colors.AMBER, alignment=ft.alignment.center),
    ]

    drone1_column = ft.Column(
        [
            ft.Text(value="Drone #1", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align = ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Column(
                    drone1_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
        ]
    )

    drone2_items = [
        ft.Container( width=200, height=75, content=ft.Text("Launch"), on_click=drone2_launch, bgcolor = ft.colors.GREEN_200, alignment=ft.alignment.center), 
        ft.Container(width=200, height=75, content=ft.Text("Land"), on_click=drone2_land, bgcolor = ft.colors.CYAN_200, alignment=ft.alignment.center),
        ft.Container(width=200, height=75, content=ft.Text("Hover"), on_click=drone2_hover, bgcolor = ft.colors.AMBER, alignment=ft.alignment.center),
    ]

    drone2_column = ft.Column(
        [
            ft.Text(value="Drone #2", style=ft.TextThemeStyle.DISPLAY_SMALL, text_align = ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Column(
                    drone2_items, 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ), 
        ]
    )

    cv2window =  ft.Card(
            elevation=30,
            content=ft.Container(
                bgcolor=ft.colors.WHITE24,
                padding=10,
                border_radius = ft.border_radius.all(20),
                content=ft.Column([
                    Countdown,
                    ft.Text("OPENCV WITH FLET",
                         size=20, weight="bold",
                         color=ft.colors.WHITE),
                ]
                ),
            )
    )

    page.add(
        ft.Row(
            [
                drone1_column,
                drone2_column,
                cv2window
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        ),

        ft.Row(
            controls=[
            ft.Container(width=415, height=75, content=ft.Text("ORDER 66"), on_click=order66, bgcolor = ft.colors.RED, alignment=ft.alignment.center)]
        )
    )

ft.app(target=main)
cv2.destroyAllWindows()