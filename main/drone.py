import djitellopy as tel
from enum import Enum

class State(Enum):
    Landed = 1
    Takeoff = 2
    Explore = 3
    FollowWalkway = 4
    FollowHallway = 5
    TrackPerson = 6
    Doorway = 7

class Drone(tel.Tello):
    vidCap = []
    state = State.Landed
    
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.connect()
        self.streamon()
        self.vidCap = self.get_video_capture()

    def getFrame(self):
        return self.vidCap.read()

    def stop(self):
        self.vidCap.release()
        self.streamoff()
        self.end()

    def move(di):
        

    