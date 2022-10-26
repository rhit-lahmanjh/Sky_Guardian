import djitellopy as tel

class Swarm(tel.swarm):
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