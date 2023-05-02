#!/bin/env python
from drone import (Drone, State)
from behaviors.behavior import behavior1
import flet as ft
import djitellopy
import socket
import time
import numpy as np
from yoloClasses import vision_class
import cv2
import base64
import threading
from flet import * 

# tello_address = ('192.168.10.1', 8889)
# local_address = ('', 9000)
        
def main(page: ft.Page):
    # drone connection
    alphaIP = '192.168.0.140'
    alphaCmdPort = 8889
    local1_address = ('192.168.0.245',9010)
    drone1 = Drone(identifier = 'chuck',behavior = behavior1(),tello_ip=alphaIP)

    # drone1 = Drone(identifier = 'test', behavior = None)
    cap = drone1.sensoryState.videoCapture

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
        drone1.opState = State.Land
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

        # opening the file in read mode

    object_list = [e.name for e in vision_class]

    reaction_data = ["flipOnBanana", "bobOnScissors", "pauseOnSoccerBall", "followCellPhone", "RunFromBanana"]

    class ReactionInput(ft.UserControl):
        def __init__(self, droneName):
            super().__init__()
            self.droneName = droneName

        def build(self):
            self.resultdata = ListView()
            self.resultlist = resultlist =  ft.Card(
                content=ft.Container(
                    width=500,
                    content=ft.Column([],spacing=0),
                    padding=ft.padding.symmetric(vertical=10),
                    )
            )
            self.resultcon = Container(
                bgcolor="red200",
                padding=10,
                margin=10,
                offset=transform.Offset(-2,0),
                animate_offset = animation.Animation(600,curve="easeIn"),
                content=Column([self.resultdata])
            )
            self.t1 = ft.Text()
            self.t2 = ft.Text()
            
            self.b = ft.ElevatedButton(text="Submit", on_click=self.button_clicked)
            self.dd = ft.Dropdown(
                width=300,
                options=[]
            )
            
            for item in reaction_data:
                self.dd.options.append(ft.dropdown.Option(str(item)))
                
            # HIDE RESULT FOR YOU SEARCH DEFAULT
            self.resultcon.visible = False

            self.txtsearch = TextField(label="Input object from COCO dataset",on_change=self.searchnow, on_submit=self.getresult)
            
            return ft.Card( 
                    content=ft.Container(
                    content=ft.Column(
                    [
                        Text(self.droneName, size=30,weight="bold"),
                        self.txtsearch,
                        self.resultcon,
                        ft.Column([
                            self.dd, self.b
                        ])
                    ]
                    ),
                    width=400,
                    padding=10,
                    )
        )
        
        def getresult(self, e):
            self.resultcon.offset = transform.Offset(-2,0)
            self.resultdata.controls.clear()
            page.update()
                
            self.mysearch = e.control.value
            self.result = []

            # IF NOT BLANK YOU TEXTFIELD SEARCH THE RUN FUNCTION
            if not self.mysearch == "":
                for item in object_list:
                    if self.mysearch in item:
                        self.result.append(item)
            
            self.t1.value = f"Object selected: {self.result[0]}"
            
        def searchnow(self,e):
            self.mysearch = e.control.value
            result = []

            # IF NOT BLANK YOU TEXTFIELD SEARCH THE RUN FUNCTION
            if not self.mysearch == "":
                self.resultcon.visible = True
                for item in object_list:
                    if self.mysearch in item:
                        self.resultcon.offset = transform.Offset(0,0)
                        result.append(item)
                page.update()

            # IF RESULT THERE DATA THEN PUSH DATA TO WIDGET CONTAINER Resultcon
            if result:
                self.resultdata.controls.clear()
                print(f"Your result {result}")
                for x in result[:3]:
                    self.resultdata.controls.append(
                    Text(x, size=20,color="white")
                        )
                page.update()
                
            else:
                self.resultcon.offset = transform.Offset(-2,0)
                self.resultdata.controls.clear()
                page.update()
                
        def button_clicked(self, e):
            self.t2.value = f"Reaction selected: {self.dd.value}"
            page.update()
    # # CV2 Window 
    # class Countdown(ft.UserControl):
    #     def __init__(self):
    #         super().__init__()

    #     def did_mount(self):
    #         self.update_timer()

    #     def update_timer(self):
    #         while True:
    #             drone1.sensoryState.__clearBuffer__(drone1.sensoryState.videoCapture)
    #             _, frame = drone1.sensoryState.videoCapture
    #             # frame = cv2.resize(frame,(400,400))
    #             _, im_arr = cv2.imencode('.png', frame)
    #             im_b64 = base64.b64encode(im_arr)
    #             self.img.src_base64 = im_b64.decode("utf-8")
    #             self.update()

    #             # img_b64 = drone1.sensoryState.image
    #             # print(type(drone1.sensoryState.image))
    #             # # img_b64 = ndarray_to_b64(np.array(drone1.sensoryState.image).astype('uint8'))
    #             # self.img = drone1.sensoryState.image
    #             # self.update()

    #     def build(self):
    #         self.img = ft.Image(
    #             border_radius=ft.border_radius.all(20)
    #         )
    #         return self.img

    # def ndarray_to_b64(ndarray):
    # # converts a np ndarray to a b64 string readable by html-img tags 
    #     img = cv2.cvtColor(ndarray, cv2.COLOR_RGB2BGR)
    #     _, buffer = cv2.imencode('.png', img)
    #     return base64.b64encode(buffer).decode('utf-8')

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

    ft.IconButton(
                    icon=ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED,
                    icon_color="blue400",
                    icon_size=20,
                    tooltip="Pause record",
                ),

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
                    # Countdown(drone1),
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
                # cv2window
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        ),

        ft.Row(
            controls=[
            ft.Container(width=415, height=75, content=ft.Text("ORDER 66"), on_click=order66, bgcolor = ft.colors.RED, alignment=ft.alignment.center)]
        ), 

        ReactionInput("Drone 1"),
    )

ft.app(target=main)
cv2.destroyAllWindows()

# class Countdown(ft.UserControl, Drone):
#     cv2.namedWindow("Video Stream",cv2.WINDOW_NORMAL)
#     cv2.resizeWindow("Video Stream", 400, 600)
#     cap = Drone.sensoryState.videoCapture
    
#     myImage = ft.Image(src=False, width=300, height=300, fit="cover")
# 		# # AND SAVE THE FILE NAME WITH TIME NOW 
# 		# timestamp = str(int(time.time()))
# 		# myfileface = str("myCumFaceFile" + "_" + timestamp + '.jpg')
#     try:
#         while True:
#             ret, frame = cap.read()
#             cv2.imshow("Webcam",frame)
#             myImage.src = ""
#             ft.page.update()

#             # AFTER THAT WAITING YOU INPUT FROM KEYBOARD
#             key = cv2.waitKey(1)

#             # AND IF YOU PRESS Q FROM YOU KEYBOARD THEN
#             # THE WEBCAM WINDOW CAN CLOSE 
#             # AND YOU NOT CAPTURE YOU IMAGE
#             # if key == ord("q"):
#             #     break
#             # elif key == ord("s"):
#             #     # AND IF YOU PRESS s FROM YOU KEYBOARD
#             #     # THE THE YOU CAPTURE WILL SAVE IN FOLDER YOUPHOTO
#             #     cv2.imwrite(f"youphoto/{myfileface}",frame)
#             #     # AND SHOW TEXT YOU PICTURE SUCCESS INPUT
#             #     cv2.putText(frame,"YOU SUCESS CAPTURE GUYS !!!",(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
#             #     cv2.imshow("Webcam",frame)
#             #     cv2.waitKey(3000)
#             #     folder_path = "youphoto/"
#             #     myimage.src = folder_path + myfileface
#             #     page.update()
#             #     break
            
#             cap.release()
#             cv2.destroyAllWindows()
#             ft.page.update()    

#     except Exception as e:
#         print(e)
#         print("Failed")