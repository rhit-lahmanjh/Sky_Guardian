import time as t
from collections import deque
import numpy as np




class RefreshTracker():
    refreshRateQueue = None
    lastTimeMark = None
    maxRefresh = 0
    minRefresh = 0
    NUM_STORED_POINTS = 50

    def __init__(self) -> None:
        self.refreshRateQueue = deque()
        self.lastTimeMark = t.time()
    
    def update(self):
        currentTimeMark = t.time()
        # print(f"Current Period: {currentTimeMark-self.lastTimeMark}")
        currentRate = 1/(currentTimeMark - self.lastTimeMark)
        self.refreshRateQueue.append(currentRate)
        if(len(self.refreshRateQueue) > self.NUM_STORED_POINTS):
            self.refreshRateQueue.popleft()
        self.lastTimeMark = currentTimeMark

    def getRate(self, max = False, average = False):
        if max:
            return max(self.refreshRateQueue)
        if average:
            return np.average(self.refreshRateQueue)
        return self.refreshRateQueue[-1]

    def print(self):
        print(f"Last Refresh Rate: {self.refreshRateQueue[-1]}\nMax Refresh Rate: {np.max(self.refreshRateQueue)}\nMinimum Refresh Rate: {np.min(self.refreshRateQueue)}\nAverage Refresh Rate: {np.average(self.refreshRateQueue)}")

    def printAVG(self):
        print(f"Average Refresh Rate: {np.average(self.refreshRateQueue)}")