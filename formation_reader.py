import numpy as np
import time
from vpython import *

data = np.load("history.npy", allow_pickle=True)

scene.width = data[len(data)-1][1]
scene.height = data[len(data)-1][2]
scene.range =200 #data[len(data)-1][3]
#scene.autoscale = True
Vsun = sphere(pos=vector(0,0,0),radius=data[len(data)-1][0],color=color.yellow)
visual_bodies = []

for i in range(len(data)-1):
    visual_bodies.append(sphere(radius=data[0][0],color=color.blue,visible=False))

while True:
    for t in range(len(data[0][1])):
        scene.caption=("Time: ",t)
        for i in range(len(data)-1):
            if data[i][1][t] != None:
                visual_bodies[i].visible = True
                visual_bodies[i].pos = vector(data[i][1][t][0], data[i][1][t][1], data[i][1][t][2])
                visual_bodies[i].radius = data[i][0]
            else:
                visual_bodies[i].visible = False
        time.sleep(0.1)
