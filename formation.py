from vpython import *
import argparse
import numpy as np
from tqdm import tqdm
import time

def mag(vector):
    return ((vector[0]**2)+(vector[1]**2)+(vector[2]**2))**0.5

def rel_pos(obj1, obj2):
    return [obj1.pos[0] - obj2.pos[0], obj1.pos[1] - obj2.pos[1], obj1.pos[2] - obj2.pos[2]]

def radians(degrees):
    return degrees*(np.pi/180)

def degrees(radians):
    return radians*(180/np.pi)

def perp_vector(vector, normalize):
    c1 = np.random.randint(-100, 100)
    c2 = np.random.randint(-100, 100)
    new_vec = [c1, c2, -1*(1/vector[2])*((vector[0]*c1)+(vector[1]*c2))]
    if not normalize:
        return new_vec
    if normalize:
        m = mag(new_vec)
        return [new_vec[0]/m, new_vec[1]/m, new_vec[2]/m]

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

def collision(obj1, obj2, new_ID):
    new_obj = Body(new_ID,0,0,0)
    new_obj.mass = obj1.mass + obj2.mass
    new_obj.size = (((obj1.size**3)+(obj2.size**3))**(1/3))*0.75

    new_obj.pos[0] = (obj1.pos[0]+obj2.pos[0])/2
    new_obj.pos[1] = (obj1.pos[1]+obj2.pos[1])/2
    new_obj.pos[2] = (obj1.pos[2]+obj2.pos[2])/2

    new_vel_mag = (1/(obj1.mass+obj2.mass))*(((((obj1.mass*obj1.velocity[0])+(obj2.mass*obj2.velocity[0]))**2)+(((obj1.mass*obj1.velocity[1])+(obj2.mass*obj2.velocity[1]))**2)+(((obj1.mass*obj1.velocity[2])+(obj2.mass*obj2.velocity[2]))**2))**0.5)
    old_vel_sum = [(obj1.velocity[0]+obj2.velocity[0]), (obj1.velocity[1]+obj2.velocity[1]), (obj1.velocity[2]+obj2.velocity[2])]
    old_vel_sum_mag = mag(old_vel_sum)
    new_vel_dir = [old_vel_sum[0]/old_vel_sum_mag, old_vel_sum[1]/old_vel_sum_mag, old_vel_sum[2]/old_vel_sum_mag]
    new_obj.velocity = [new_vel_dir[0]*new_vel_mag, new_vel_dir[1]*new_vel_mag, new_vel_dir[2]*new_vel_mag]

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

    def __init__(self, ID, r, theta, phi):
        # Initial conditions
        self.ID = ID
        self.r = r
        self.theta = radians(theta)
        self.phi = radians(phi)
        self.alive = True
        # Physical attributes
        self.pos = [self.r*np.cos(self.theta)*np.sin(self.phi), self.r*np.sin(self.theta)*np.sin(self.phi), self.r*np.cos(self.phi)]
        self.velocity = []
        self.mass = 1
        self.size = 1
        return

    def put_in_orbit(self, orbiting):

        vel_mag = ((G*orbiting.mass)/mag(rel_pos(self, orbiting)))**0.5
        direction = perp_vector(rel_pos(self, orbiting), True)
        self.velocity = [direction[0]*vel_mag, direction[1]*vel_mag, direction[2]*vel_mag]

        return

def initialize(G, sun_size, sun_mass, p_size, p_mass, p_start, p_end, particle_num, output_name):

    bodies = []
    world_history = []

    sun = Body("s",0, 0, 0)
    sun.pos = [0, 0, 0]
    sun.mass = sun_mass
    sun.size = sun_size

    print('Initializing simulation...')

    positions = []

    for i in range(particle_num):
        positions.append([np.random.randint(p_start, p_end), np.random.randint(0,500), np.random.randint(0,1000)])

    for p in tqdm(positions):
        body = Body(len(world_history), p[0], p[1], p[2])
        body.mass = p_mass
        body.size = p_size
        body.put_in_orbit(sun)
        safe = True
        for other in bodies:
            if hitbox(body, other):
                safe = False
                break
        if safe:
            bodies.append(body)
            world_history.append([body.size, [body.pos]])

    bodies.append(sun)
    output = [bodies, world_history, G]
    np.save(output_name+"_setup", np.asarray(output, dtype=object))

    return output

def simulate(input_file, sim_duration, output_name):

    input = np.load(input_file, allow_pickle=True)

    bodies = input[0]
    sun = bodies[-1]
    bodies = [bodies[i] for i in range(len(bodies)-1)]
    world_history = input[1]
    G = input[2]

    print('Simulating...')
    save_times = [int(np.floor((sim_duration/10)*i)) for i in range(1,10)]
    for t in tqdm(range(sim_duration)):

        for i in range(len(bodies)):
            body = bodies[i]
            if hitbox(body, sun):
                body.alive = False
                sun.mass += body.mass

            if body.alive:
                a_net = [0, 0, 0]
                for j in range(len(bodies)):
                    other = bodies[j]
                    if i != j and other.alive:
                        if hitbox(body, other):
                            new_obj = collision(body, other, len(world_history))
                            bodies.append(new_obj)
                            world_history.append([new_obj.size, [None for q in range(t+1)]])
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
                while len(world_history[body.ID][1]) < sim_duration+1:
                    world_history[body.ID][1].append(None)
            else:
                world_history[body.ID][1].append([body.pos[0], body.pos[1], body.pos[2]])
            i += 1

        if t in save_times:
            np.save("simulation"+"_sim", np.asarray([world_history, sun.size], dtype=object))

    np.save(output_name+"_sim", np.asarray([world_history, sun.size], dtype=object))

    return [world_history, sun.size]

def play(input_file):

    input = np.load(input_file, allow_pickle=True)

    data = input[0]
    sun_size = input[1]

    scene.autoscale = True
    Vsun = sphere(pos=vector(0,0,0),radius=sun_size,color=color.yellow)
    visual_bodies = []

    for i in range(len(data)):
        visual_bodies.append(sphere(radius=data[0][0],color=color.blue,visible=False))

    while True:
        for t in range(len(data[0][1])):
            scene.caption=("Time: ",t)
            for i in range(len(data)):
                if data[i][1][t] != None:
                    visual_bodies[i].visible = True
                    visual_bodies[i].pos = vector(data[i][1][t][0], data[i][1][t][1], data[i][1][t][2])
                    visual_bodies[i].radius = data[i][0]
                else:
                    visual_bodies[i].visible = False
            time.sleep(0.1)

    return

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['setup','simulate','play'], help='choose from the following modes: setup, simulate, or play.')
args = parser.parse_args()
mode = args.mode

if mode == 'setup':
    custom = input('Would you like to use custom settings (yes or no)? ')
    if custom == 'yes':
        G = float(input('gravitational constant (default=0.08): '))
        sun_size = float(input('sun radius (default=20): '))
        sun_mass = float(input('sun mass (default=100000): '))
        p_size = float(input('paricle radius (default=2) '))
        p_mass = float(input('particle mass (default=1) '))
        p_start = int(input('starting radius for particles (default=150): '))
        p_end = int(input('ending radius for particles (default=201): '))
        particle_num = float(input('number of particles (default=500): '))
    elif custom == 'no':
        G = 0.008
        sun_size = 20
        sun_mass = 100000
        p_size = 2
        p_mass = 1
        p_start = 150
        p_end = 201
        particle_num = 500
    output_name = input('output file name: ')
    data = initialize(G, sun_size, sun_mass, p_size, p_mass, p_start, p_end, particle_num, output_name)
    print('initilization complete.')
    view = input('would you like to view the initial conditions (yes or no)? ')
    if view == 'yes':
        for i in range(len(data[0])-1):
            body = data[0][i]
            Vbody = sphere(radius=body.size,color=color.blue)
            Vbody.pos = vector(body.pos[0], body.pos[1], body.pos[2])
        Vsun = sphere(pos=vector(0,0,0),radius=sun_size,color=color.yellow)

elif mode == 'simulate':
    input_file = input('setup file: ')
    G = np.load(input_file, allow_pickle=True)[2]
    sim_duration = int(input('number of iterations in simulation: '))
    output_name = input('output file name: ')
    simulate(input_file, sim_duration, output_name)
    print('simulation complete.')

elif mode == 'play':
    input_file = input('simulation file: ')
    play(input_file)
