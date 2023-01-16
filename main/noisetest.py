from perlin_noise import PerlinNoise
import numpy as np

noise = PerlinNoise(octaves=7,seed=1)
print(np.zeros((,1)))

prevDirection = np.array([0.001,.5,0.001,0.001]) # this is not default argument bc using self
for i in range(0,10):
    print(f'Previous {prevDirection}')
    n1 = noise(prevDirection[0])
    n2 = noise(prevDirection[1])
    n3 = noise(prevDirection[2])
    n4 = noise(prevDirection[3])
    print(f'Noise: {n1},{n2},{n3},{n4}')
    prevDirection = np.add(prevDirection,np.array([n1,n2,n3,n4]))
    # mag = direction[0]**2 + direction[1]**2 + direction[2]**2 + direction[3]**2
    mag = 10.0/np.linalg.norm(prevDirection)
    prevDirection = prevDirection*mag
    print(f'Sum {prevDirection}')
