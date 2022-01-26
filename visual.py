from vpython import *

rod = cylinder(color=color.blue,pos=vector(0,2,1),axis=vector(5,0,0), radius=1)
cone = cone( color=color.cyan,pos=vector(3,4,0),axis=vector(12,0,0),radius=1)
box = box(pos=vector(5,3,0),length=20,height=10,width=2)
sphere = sphere(pos=vector(0,7,0),color=color.red)
count=0
goUp=True

while(True):
    rate(10)
    if(goUp):
        count=count+1
    else:
        count=count-1

    rod.pos = vector(0+count,2-count,1)
    cone.pos = vector(10-count,count+1,0)
    box.pos = vector(5+count*-2,3,count)
    sphere.pos = vector(count*-5,count,count)

    if(count==10):
        goUp=False
    if(count==0):
        goUp=True
