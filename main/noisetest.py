from perlin_noise import PerlinNoise
import numpy as np
import math

np.printoptions(precision=2,floatmode='unique')

counter = 0
maxSpeed = 40
noise = PerlinNoise(octaves=15,seed=1)
# print(np.zeros((,1)))
xStart = .3
zStart = 0
yawStart = 0
yStart = math.sqrt(1 - xStart**2 - zStart**2 - yawStart**2)
xyNoise = .1
theta = 0.1
clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

prevDirection = np.array([xStart,yStart,zStart,yawStart]) # this is not default argument bc using self
prevDirection = prevDirection*maxSpeed
for i in range(0,1000):
    if counter == 10:
        # print(f'Previous {prevDirection}')
        # prevDirection = np.divide(prevDirection,maxSpeed)
        xyNoise = noise(xyNoise)
        # print(xyNoise)
        noiseSpin = math.pi * xyNoise
        theta = theta + noiseSpin
        theta = clamp(theta,-math.pi/2,math.pi/2)

        xDir = math.cos(theta)
        yDir = abs(math.sin(theta))

        # n2 = noise(prevDirection[1])
        # n3 = noise(prevDirection[2])
        # n4 = noise(prevDirection[3])
        # noiseVec = np.array([n1,n2,n3,n4]) * 
        # print(f'Noise: {n1},{n2},{n3},{n4}')
        prevDirection = np.array([xDir,yDir,0,xDir]) # this is not default argument bc using self
        # prevDirection = np.add(prevDirection)
        # mag = direction[0]**2 + direction[1]**2 + direction[2]**2 + direction[3]**2
        movementVec = prevDirection*maxSpeed
        counter = 0
        print(f'Sum {movementVec}')
    counter += 1
    print(counter)


for i in range(0,1000):
    if counter == 10:
        xyNoise = noise(xyNoise)
        theta = clamp(theta + (math.pi * xyNoise))

        xDir = math.cos(theta)
        yDir = abs(math.sin(theta))

        prevDirection = np.array([xDir,yDir,0,xDir]) # this is not default argument bc using self

        movementVec = prevDirection*maxSpeed
        counter = 0
        print(f'Sum {movementVec}')
    counter += 1
    print(counter)

        # def __randomWander__(self):
    #     """Shifts a random movement vector smoothly by applying Perlin noise.
    #     Args:
    #         prevDirection (_type_, optional): _description_. Defaults to None.
    #     Returns:
    #         _type_: _description_
    #     """
    #     # if self.firstTakeoff: 
    #     #     self.prevDirection = np.array([0.5,.5,.5,0]) # this is not default argument bc using self
    #     #     self.firstTakeoff = False
    #     # else:
    #     #     self.prevDirection = self.prevDirection/self.MAXSPEED

    #     print(f'Previous {self.prevDirection}')
    #     noiseVec = self.noiseGenerator(self.prevDirection)
    #     # n1 = self.noise(self.prevDirection[0])
    #     # n2 = self.noise(self.prevDirection[1])
    #     # n3 = self.noise(self.prevDirection[2])
    #     # n4 = self.noise(self.prevDirection[3])
    #     # self.prevDirection = np.add(self.prevDirection,np.array([n1,n2,n3,n4]))
    #     self.prevDirection = np.add(self.prevDirection,noiseVec)

    #     mag = self.MAXSPEED/np.linalg.norm(self.prevDirection)
    #     self.prevDirection = self.prevDirection*mag
    #     print(f'Sum {self.prevDirection}')
    #     # self.prevDirection = self.prevDirection
    #     return self.prevDirection