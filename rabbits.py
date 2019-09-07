from vpython import *
import random

scene.width = 1000
scene.height = 800
scene.range = 500

max_left = -450
max_right = 450

ground = box(pos=vector(0,-560,0),length=10000000,height=1100,width=100,color=color.green)
sky = box(pos=vector(0,0,-100),length=10000000,height=1000000,width=0,color=color.cyan)

buns = list()
for q in range(1):

    x = random.randint(max_left,max_right)
    rad = 20

    bun_id = q
    bun = sphere(pos=vector(x,0,0),radius=rad,color=color.white)
    bun.velocity = vector(0,0,0)
    family = list()
    mates = list()

    pack = [bun_id,bun,bun.velocity,family,mates]
    buns.append(pack)

dt = 2

while True:

    scene.caption=("Number of buns: ",len(buns))

    rate(100)
    switch = 1

    for anim in buns:
        
        bun_id = anim[0]
        bun = anim[1]
        bun_velocity = anim[2]
        family = anim[3]
        mates = anim[4]

        # Move bun:

        if bun.pos.y >= 0:
            g = -0.01
            bun.velocity = vector(bun.velocity.x,bun.velocity.y + g,0)
            bun.pos = bun.pos + (bun.velocity*dt)

        # Hop bun:

        elif bun.pos.y < 0:
            bun.velocity = (0,0,0)

            n = random.randint(1,500)
            if n == 1:

                if max_left < bun.pos.x < max_right:
                    bun.velocity = vector(random.randint(-1,1)/random.randint(1,3),1,0)
                    bun.pos = bun.pos + (bun.velocity*dt)

                elif bun.pos.x < max_left:
                    bun.velocity = vector(random.randint(1,2),1,0)
                    bun.pos = bun.pos + (bun.velocity*dt)

                elif bun.pos.x > max_right:
                    bun.velocity = vector(random.randint(-2,-1),1,0)
                    bun.pos = bun.pos + (bun.velocity*dt)

            for other in buns:

                other_id = other[0]
                other_obj = other[1]
                ofam = other[3]
                omates = other[4]

                if mag(bun.pos - other_obj.pos) <= (2*rad) and bun_id != other_id and other_obj.pos.y < 0:

                    if bun_id not in ofam and bun_id not in omates:
                        if other_id not in family and other_id not in mates:

                            mates.append(other_id)
                            omates.append(bun_id)

                            litter = random.randint(1,4)

                            for b in range(litter):
                                if switch == 1 and len(buns) < 200:
                    
                                    newloc = (bun.pos + other_obj.pos) / 2

                                    newbun_id = buns[len(buns)-1][0] + 1
                                    newbun = sphere(pos=newloc,radius=rad,color=color.white)
                                    newbun.velocity = vector(0,0,0)
                                    newfamily = list()
                                    newmates = list()

                                    for i in family:
                                        newfamily.append(i)
                                    for j in ofam:
                                        newfamily.append(j)

                                    newpac = [newbun_id,newbun,newbun.velocity,newfamily,newmates]
                                    buns.append(newpac)

                                    family.append(newbun_id)
                                    ofam.append(newbun_id)

                                    if b == litter - 1:
                                        switch = 0

                                else:
                                    continue

              
