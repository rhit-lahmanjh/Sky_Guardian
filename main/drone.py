import djitellopy as tel

class Drone(tel.Tello):
    vidCap = []

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