from vpython import *
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

def ang_momentum(r, m, v):
    return np.cross(r, [m*v[0], m*v[1], m*v[2]])

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

def collision(obj1, obj2):
    new_obj = Body(len(world_history),0,0,0)
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

    if visual:
        Vbody = sphere(radius=body.size,color=color.blue)
        Vbody.pos = vector(new_obj.pos[0], new_obj.pos[1], new_obj.pos[2])
        visual_bodies.append(Vbody)
        
    
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
        self.size = 2
        return

    def put_in_orbit(self, orbiting):

        vel_mag = ((G*orbiting.mass)/mag(rel_pos(self, orbiting)))**0.5
        direction = perp_vector(rel_pos(self, orbiting), True)
        body.velocity = [direction[0]*vel_mag, direction[1]*vel_mag, direction[2]*vel_mag]

        return

 
global visual
visual = False
global G
G = 0.08

if visual:
    scene.width = 2000
    scene.height = 1000
    scene.range = 400

# Initialize
sun = Body("s",0, 0, 0)
sun.pos = [0, 0, 0]
sun.mass = 100000
sun.size = 20
ini_sun_size = sun.size
if visual:
    Vsun = sphere(pos=vector(0,0,0),radius=sun.size,color=color.yellow)

bodies = []
world_history = []
visual_bodies = []

print('Initializing simulation...')
r = 150
while r < 200:
    ini_theta = np.random.randint(0,359)
    theta = ini_theta
    while theta < 360 + ini_theta:
        ini_phi = np.random.randint(0,359)
        phi = ini_phi
        while phi < 360 + ini_phi:
            body = Body(len(world_history), r, theta, phi)
            body.put_in_orbit(sun)
            safe = True
            for other in bodies:
                if hitbox(body, other):
                    safe = False
            if safe:
                bodies.append(body)
                world_history.append([body.size, [body.pos]])
                
                if visual:
                    Vbody = sphere(radius=body.size,color=color.blue)
                    Vbody.pos = vector(body.pos[0], body.pos[1], body.pos[2])
                    visual_bodies.append(Vbody)
            
            phi += degrees(((bodies[0].size*2)+50)/r)
        theta += degrees(((bodies[0].size*2)+50)/r)
    r += (bodies[0].size*2)+50
 
print('Initialization complete. Simulation contains',len(bodies),'particles.')
print('')
print('Simulating...')

# Update and draw
sim_duration = 2000
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
                        new_obj = collision(body, other)
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
                
            if visual:
                visual_bodies[i].visible = False
                
        else:
            world_history[body.ID][1].append([body.pos[0], body.pos[1], body.pos[2]])
            
            if visual:
                visual_bodies[i].pos = vector(body.pos[0], body.pos[1], body.pos[2])
            
        i += 1
     
    #time.sleep(0.01)

print('Done!')
world_history.append([ini_sun_size, scene.width, scene.height, scene.range])
np.save("history", np.asarray(world_history, dtype=object))
