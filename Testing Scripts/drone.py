import djitellopy as tel
from enum import Enum

class NavState(Enum):
    Landed = 1
    Takeoff = 2
    Explore = 3
    FollowWalkway = 4
    FollowHallway = 5
    TrackPerson = 6
    Doorway = 7

class Drone(tel.Tello):
    vidCap = []
    navState = NavState.Landed
    status = []
    
    def __init__(self,name,stream):
        super().__init__()
        self.name = name
        self.connect()
        if(stream):
            self.streamon()
            self.vidCap = self.get_video_capture()

    def getFrame(self):
        return self.vidCap.read()

    def stop(self):
        self.vidCap.release()
        self.streamoff()
        self.end()

    def update_current_state(self):
        """Updates the state of all the sensors on the drone and stores it."""
        self.status = self.get_current_state()
    
    def get_sensor_reading(sensor):
        """Gets a specific sensor reading based on key:
        baro = the barometer measurement in cm.
        tof = the time of flight distance in cm.
        pitch = the degree of the attitude pitch.
        roll = the degree of the attitude roll.
        yaw = the degree of the attitude yaw.
        vgx = the speed of “x” axis.
        vgy = the speed of the “y” axis.
        vgz = the speed of the “z” axis.
        templ = the lowest temperature in degree Celsius.
        temph = the highest temperature in degree Celsius
        h = the height in cm.
        bat = the percentage of the current battery level.
        time = the amount of time the motor has been used.
        agx = the acceleration of the “x” axis.
        agy = the acceleration of the “y” axis.
        agz = the acceleration of the “z” axis."""
        return self.status[sensor]


        

    