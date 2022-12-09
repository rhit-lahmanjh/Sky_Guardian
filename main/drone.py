import sys
import djitellopy as tel
from enum import Enum
from perlin_noise import PerlinNoise
from feedAnalyzer import FeedAnalyzer
import cv2
import keyboard as key
import time as t
import socket 

DEBUG_PRINTS = False
WITH_DRONE = False

class State(Enum):
    Landed = 1
    Takeoff = 2
    Explore = 3
    FollowWalkway = 4
    FollowHallway = 5
    TrackPerson = 6
    Doorway = 7
    Scan = 8
    Hover = 9

class Drone(tel.Tello):
    vidCap = None
    MAXSPEED = 10
    state = None
    prevState = None
    noise = None
    vision = None
    STOP = [0,0,0,0]
    
    
    def __init__(self,name):
        cv2.VideoCapture()
        super().__init__()
        self.name = name
        self.state = State.Landed
        if WITH_DRONE:
            # This is where we will implement connecting to a drone through the router
            self.connect()
            self.set_speed(self.MAXSPEED)

            #setup video
            self.streamon()
            self.vidCap = self.get_video_capture()
            self.VID_UDP_ADD = self.get_udp_video_address()

        #setup useful classes
        self.noise = PerlinNoise()
        self.vision = FeedAnalyzer()

    def clear_buffer(self, cap):
        """ Emptying buffer frame """
        while True:
            start_time = t.time()
            grabbed = cap.grab()
            if t.time()-start_time > .02:
                break
            
    def getFrame(self):
        self.clear_buffer(self.vidCap)
        return self.vidCap.retrieve()

    def stop(self):
        print('Stopping')
        if self.is_flying:
            self.land()
        self.vidCap.release()
        self.streamoff()
        self.end()   

    def moveDirection(self,direction = [0, 0, 0, 0]):
        """Set the speed of the drone based on xyz and yaw
        direction is:
        forward/backward : x or element 1
        side to side     : y or element 2
        up and down      : z or element 3
        yaw              : turn or element 4
        """
        cmd = f'rc {direction[1]} {direction[0]} {direction[2]} {direction[3]}'    
        self.send_command_without_return(cmd)

    def randomWander(self,prevDirection = None):
        """Shifts a random movement vector smoothly by applying Perlin noise
        """
        if prevDirection == None:
            prevDirection = [0,self.MAXSPEED/2,0,0] # this is not default argument bc using self
        print(f'Previous {prevDirection}')
        noise = self.noise(prevDirection)
        print(f'Noise{noise}')
        direction = prevDirection + noise
        print(f'Sum{direction}')
        return direction
    
    def fullScan(self):
        self.moveDirection([0,0,0,10])

    def handleUserInput(self):
        # land interrupt
        if(key.is_pressed('l')):
            self.land()
            self.state = State.Landed
            return
        moveDist = 30
        if key.is_pressed('up'):
            self.move_up(60)
            return
        if key.is_pressed('f'):
            self.flip_back()
            return
        if key.is_pressed('down'):
            self.move_down(moveDist)
            return
        if key.is_pressed('a'):
            self.move_left(moveDist)
            return
        if key.is_pressed('d'):
            self.move_right(moveDist)
            return
        if key.is_pressed('w'):
            self.move_forward(moveDist)
            return
        if key.is_pressed('s'):
            self.move_back(moveDist)
            return
        if key.is_pressed('left'):
            self.rotate_counter_clockwise(45)
            return
        if key.is_pressed('right'):
            self.rotate_clockwise(45)
            return

    def test(self):
        while cv2.waitKey(20) != 27: # Escape
            self.randomWander()


    def operate(self):
        # creating window
        if(WITH_DRONE):
            cv2.namedWindow('test', cv2.WINDOW_NORMAL)
     

        # general loop
        while cv2.waitKey(20) != 27: # Escape
            if DEBUG_PRINTS:
                print("looping")

            #INSERT TELEMETRY CHECKS
            
            # get and analyze visual stimulus
            returned, img = self.getFrame()
            if returned:
                print('Seeing')
                objects = self.vision.detect_objects(img)
                self.vision.display_objects(img, objects,threshold=.9)
                cv2.imshow('test', img)

                # initial demo IO, soon to be removed
                for object in objects[0,0,:,:]:
                    if object[2] < .8:
                        break
                    if object[1] == 77:
                        cellPhoneCounter = cellPhoneCounter + 1
                    if object[1] == 77 and cellPhoneCounter == 2:
                        # self.prevState = self.state
                        # self.state = State.Hover
                        # self.flip_back()
                        print(f'Cell Phone detected. Flipping')
                        cellPhoneCounter = 0
                        break

            self.handleUserInput()

            #State Switching SIILL IN DEV
            match self.state:
                case State.Landed:
                    if key.is_pressed('t'):
                        self.state = State.Takeoff
                    print('Landed')
                case State.Takeoff:
                    self.takeoff()
                    self.state = State.Scan
                    print('Takeoff')
                case State.Scan:
                    # self.fullScan()
                    print('do nothing')
                case State.Explore:
                    self.moveDirection(self.randomWander())
                case State.Hover():
                    self.moveDirection(self.STOP)
        self.stop()
        cv2.destroyAllWindows()

drone1 = Drone('chuck')
drone1.test()