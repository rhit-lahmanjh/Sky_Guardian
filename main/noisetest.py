from perlin_noise import PerlinNoise
import numpy as np
import math

np.printoptions(precision=2,floatmode='unique')

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
for i in range(0,100):
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
    prevDirection = np.array([xDir,yDir,0,0]) # this is not default argument bc using self
    # prevDirection = np.add(prevDirection)
    # mag = direction[0]**2 + direction[1]**2 + direction[2]**2 + direction[3]**2
    movementVec = prevDirection*maxSpeed
    print(f'Sum {movementVec}')
