from vpython import *
import numpy as np
from tqdm import tqdm
import time

def mag(vector):
    return ((vector[0]**2)+(vector[1]**2)+(vector[2]**2))**0.5

def rel_pos(obj1, obj2):
    return [obj1.pos[0] - obj2.pos[0], obj1.pos[1] - obj2.pos[1], obj1.pos[2] - obj2.pos[2]]

def gravitate(gravitee, gravitator):
    r = rel_pos(gravitee, gravitator)
    r_mag = mag(r)
    a_mag = ((G * gravitator.mass) / (r_mag**2))
    return [-1 * a_mag * (r[0] / r_mag), -1 * a_mag * (r[1] / r_mag), -1 * a_mag * (r[2] / r_mag)]

def hitbox(obj1, obj2):
    if mag(rel_pos(obj1, obj2)) <= obj1.size+obj2.size:
        return True
    else:
        return False

def collision(obj1, obj2):
    new_obj = Body()
    new_obj.mass = obj1.mass + obj2.mass
    new_obj.size = ((obj1.size**3)+(obj2.size**3))**(1/3)

    new_obj.pos[0] = (obj1.pos[0]+obj2.pos[0])/2
    new_obj.pos[1] = (obj1.pos[1]+obj2.pos[1])/2
    new_obj.pos[2] = (obj1.pos[2]+obj2.pos[2])/2

    new_vel_mag = (1/(obj1.mass+obj2.mass))*(((((obj1.mass*obj1.velocity[0])+(obj2.mass*obj2.velocity[0]))**2)+(((obj1.mass*obj1.velocity[1])+(obj2.mass*obj2.velocity[1]))**2)+(((obj1.mass*obj1.velocity[2])+(obj2.mass*obj2.velocity[2]))**2))**0.5)
    old_vel_sum = [(obj1.velocity[0]+obj2.velocity[0]), (obj1.velocity[1]+obj2.velocity[1]), (obj1.velocity[2]+obj2.velocity[2])]
    old_vel_sum_mag = mag(old_vel_sum)
    new_vel_dir = [old_vel_sum[0]/old_vel_sum_mag, old_vel_sum[1]/old_vel_sum_mag, old_vel_sum[2]/old_vel_sum_mag]
    new_obj.velocity = [new_vel_dir[0]*new_vel_mag, new_vel_dir[1]*new_vel_mag, new_vel_dir[2]*new_vel_mag]

    ###
    Vbody = sphere(radius=body.size,color=color.blue)
    Vbody.pos = vector(new_obj.pos[0], new_obj.pos[1], new_obj.pos[2])
    visual_bodies.append(Vbody)
    ###
    obj1.alive = False
    obj2.alive = False
    return new_obj

def update_vecs(object, a):
    object.velocity[0] += a[0]
    object.velocity[1] += a[1]
    object.velocity[2] += a[2]
    object.pos[0] += object.velocity[0]
    object.pos[1] += object.velocity[1]
    object.pos[2] += object.velocity[2]
    return

class Body:

    def __init__(self):
        # Initial conditions
        self.r = np.random.randint(70, 500)
        self.theta = np.random.randint(0,359)
        self.phi = np.random.randint(0,359)
        self.alive = True
        # Physical attributes
        #self.pos = [self.r*np.cos(self.theta), self.r*np.sin(self.theta), 0]
        self.pos = [self.r*np.cos(self.theta)*np.sin(self.phi), self.r*np.sin(self.theta)*np.sin(self.phi), self.r*np.cos(self.phi)]
        self.velocity = []
        self.mass = 1
        self.size = 1
        return

    def put_in_orbit(self, orbiting):

        vel_mag = ((G*orbiting.mass)/mag(rel_pos(self, orbiting)))**0.5
        alpha = self.theta + (np.pi/2)
        body.velocity = [vel_mag*np.cos(alpha), vel_mag*np.sin(alpha), 0]

        return
###
scene.width = 2000
scene.height = 1000
scene.range = 1100
###
global G
G = 0.8

# Initialize
sun = Body()
sun.pos = [0, 0, 0]
sun.mass = 1
sun.size = 20
###
Vsun = sphere(pos=vector(0,0,0),radius=sun.size,color=color.yellow)
###

planet_num = 10000
bodies = []
###
visual_bodies = []
###
for i in range(planet_num):
    body = Body()
    body.put_in_orbit(sun)
    bodies.append(body)
    ###
    Vbody = sphere(radius=body.size,color=color.blue)
    Vbody.pos = vector(body.pos[0], body.pos[1], body.pos[2])
    visual_bodies.append(Vbody)
    ###

# Update and draw
sim_duration = 20000000
for i in tqdm(range(sim_duration)):

    for i in range(len(bodies)):
        body = bodies[i]
        if hitbox(body, sun):
            body.alive = False
            sun.mass += body.mass
            sun.size = ((sun.size**3)+(body.size**3))**(1/3)
        if body.alive:
            a_net = [0, 0, 0]
            for j in range(len(bodies)):
                other = bodies[j]
                if i != j and other.alive:
                    if hitbox(body, other):
                        new_obj = collision(body, other)
                        bodies.append(new_obj)
                    else:
                        a = gravitate(body, other)
                        a_net[0] += a[0]
                        a_net[1] += a[1]
                        a_net[2] += a[2]
            a_sun = gravitate(body, sun)
            a_net[0] += a_sun[0]
            a_net[1] += a_sun[1]
            a_net[2] += a_sun[2]
            update_vecs(body, a_net)

    i = 0
    while i < len(bodies):
        body = bodies[i]
        if not body.alive:
            bodies.remove(body)
            ###
            visual_bodies[i].visible = False
            visual_bodies.remove(visual_bodies[i])
            ###
        else:
            ###
            visual_bodies[i].pos = vector(body.pos[0], body.pos[1], body.pos[2])
            ###
        i += 1
        print(mag(bodies[0].pos))
        time.sleep(0.001)
