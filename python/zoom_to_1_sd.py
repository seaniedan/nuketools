####################  ZOOM TO 1_SD
#by Sean Danischevsky 2011
#zooms to 1 in the nodegraph, centered on median node position

import nuke

def zoom_to_1_sd():
    nodes = nuke.selectedNodes()
    if not nodes:
        nodes = nuke.allNodes()
        if not nodes:
            return

    #zoom to the median node
    #print [centerPos(node) for node in nodes]
    nuke.zoom( 1, medianXY([centerPos(node) for node in nodes] ))

def distance(xi, yi, xj, yj):
    #return 2d distance from xi,yi to xj,yj
    return (xi- xj)* (xi -xj)+ (yi -yj)* (yi- yj)

def centerPos(node):
    #return center point of a nuke node
    return [node.xpos()+ node.screenWidth()/ 2.0, node.ypos()+ node.screenHeight()/ 2.0]

def medianXY(listxy):
    #input= list of (x,y) 
    #return xy median

    #find mean
    centreX= sum ([i[0] for i in listxy  ])/ float(len(listxy))
    centreY= sum ([i[1] for i in listxy  ])/ float(len(listxy))

    for xy in listxy:
        #append distance to mean
        xy.append(distance(xy[0], xy[1], centreX, centreY))

    #get min distance
    newc= min(listxy, key= lambda x: x[2])

    return [ int(newc[0]), int(newc[1])]
    

#zoom_to_1_m()
#add 'zoom to 1 and and bind to 'h' key


