from vpython import *
import random
import math

scene.width = 2000
scene.height = 1000
scene.range = 1100

sun = sphere(pos=vector(0,0,0),radius=20,color=color.yellow)

planets = list()
#for q in range(10,random.randint(10,20)):
for q in range(25):
  
    G = 0.008
    M = 300000
    
    r = random.randint(150,1000)
    theta = radians(random.randint(0,365))
    phi = theta + (math.pi/2)

    x = r*math.cos(theta)
    y = r*math.sin(theta)

    m = random.randint(1,20) 
    velocity = ((G*M)/(r))**(0.5)
    
    vx = velocity*math.cos(phi)
    vy = velocity*math.sin(phi)
   
    planet_id = [q]
    planet = sphere(pos=vector(x,y,0),radius=m/2,color=color.blue,make_trail=True,retain=10)
    planet.velocity = vector(vx,vy,0)
    pack = [planet_id,planet,planet.velocity,m]
    planets.append(pack)
    
dt = 1

while True:
    
    rate(100)

    for o in planets:
        planet_id = o[0]
        planet = o[1]
        planet_velocity = o[2]
        m = o[3]
        
        # Calculate Sun's Influence:
        
        rel_pos = planet.pos - sun.pos
        r_sun = mag(rel_pos)
        Fs = (G*M*m)/(r_sun**2)
        As = (Fs/m)*(rel_pos/-r_sun)
        
        acc = list()
        acc.append(As)
        
        # Calculate All Other Influences:
        
        for obj in planets:
            if obj[0] != planet_id and planet_id not in obj[0] and obj[0] not in planet_id:
                
                other = obj[1]
                m0 = obj[3]
                
                rel_pos_obj = planet.pos - other.pos
                rprime = mag(rel_pos_obj)

                if rprime > planet.radius + other.radius:

                    F0 = (G*m0*m)/(rprime**2)
                
                    a0 = (F0/m)*(rel_pos_obj/-rprime)
                    acc.append(a0)

                elif rprime <= planet.radius + other.radius:

                    new_loc = planet.pos + ((rprime/2)*(rel_pos_obj/rprime))
                    new_mass = m + m0

                    new_id = [planet_id,obj[0]]
                    new = sphere(pos=(new_loc),radius=(new_mass/2),color=color.blue,make_trail=True,retain=10)
                    new.velocity = ((m*planet.velocity) + (m0*obj[2])) / (m + m0)

                    new_pack = [new_id,new,new.velocity,new_mass]
                    planets.append(new_pack)

                    o[1].visible = False
                    obj[1].visible = False

                    o[1].clear_trail()
                    obj[1].clear_trail()

                    planets.remove(o)
                    planets.remove(obj)

        if o in planets:
          
            Anet = vector(0,0,0)
            for a in acc:
                Anet = Anet + a

            planet.velocity = planet.velocity + Anet
            planet.pos = planet.pos + (planet.velocity*dt)

        if r_sun <= planet.radius + sun.radius:

            o[1].visible = False
            o[1].clear_trail()
            planets.remove(o)


