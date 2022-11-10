#move nodes:
#translate, rotate, scale and align Nuke nodes
#by Sean Danischevsky 2011
#scale nodes about median node in x or y
#to do: keep nodes on backdrops: 
#       if backdrop selected and empty, move it like nodes - set bd width to height etc in case of rotate. Scale width/height.
#       if backdrop selected and contains nodes, move nodes then re-size the bd after move. 
#
#
#
#to do: use grid size intelligently to place nodes on grid
#to do: scale into space remaining if there are nodes either side of selected
#to do: remove ALL nodes who we are centred on (not just in case of 1)
#to do: check we're not colliding with a node, and don't move if so

import nuke

def centerPos(node):
    #return center point of a nuke node
    return [int(node.xpos()+ node.screenWidth()/ 2.0), int(node.ypos()+ node.screenHeight()/ 2.0)]

def center_x(node):
    return int(node.xpos()+ node.screenWidth()/ 2.0)

def center_y(node):
    return int(node.ypos()+ node.screenHeight()/ 2.0)

def distance(xi, yi, xj, yj):
    #return 2d distance from xi,yi to xj,yj
    return (xi- xj)* (xi -xj)+ (yi -yj)* (yi- yj)


def median_low(data):
    """Return the low median of numeric data.
    When the number of data points is odd, the middle value is returned.
    When it is even, the smaller of the two middle values is returned.
    >>> median_low([1, 3, 5])
    3
    >>> median_low([1, 3, 5, 7])
    3
    """
    data = sorted(data)
    n = len(data)
    if n == 0:
        raise StatisticsError("no median for empty data")
    if n% 2 == 1:
        return data[n//2]
    else:
        return data[n//2 - 1]


def median(data):
    """Return the median of numeric data.
    When the number of data points is odd, the middle value is returned.
    When it is even, the average of the two middle values is returned.
    >>> median([1, 3, 5])
    3
    >>> median([1, 3, 5, 7])
    4
    """
    data = sorted(data)
    n = len(data)
    if n == 0:
        raise StatisticsError("no median for empty data")
    if n% 2 == 1:
        return data[n// 2]
    else:
        return (data[n// 2- 1]+ data[n// 2])/ 2.0

def mean(data):
    return sum (data)/ float(len(data))

def medianXY(listxy):
    #input= list of (x,y) 
    #return xy median

    #find mean
    centerX= sum ([i[0] for i in listxy])/ float(len(listxy))
    centerY= sum ([i[1] for i in listxy])/ float(len(listxy))

    for xy in listxy:
        #append distance to mean
        xy.append(distance(xy[0], xy[1], centerX, centerY))

    #get min distance
    newc= min(listxy, key= lambda x: x[2])

    return [ newc[0], newc[1]]

# Calculate good scale size
#gw= nuke.toNode("preferences")["GridWidth"].value()
#print 'gw',gw
#gh = nuke.toNode("preferences")["GridHeight"].value()

#to snap to position:
#nuke.autoplaceSnap(nuke.selectedNode())


#SCALE 
def scale_nodes(nodes, scaleX= False, scaleY= False, centerX= None, centerY= None, minmove= 20):
    import backdrop_sd

    if nodes:
        #move backdrop nodes from list to a dict {backdrop node: nodes on backdrop}
        #backdrops= {node: backdrop_sd.nodes_in_backdrop(node) for node in nodes if node.Class() == 'BackdropNode'}
        #separate nodes into 2 lists: nodes and backdrops
        backdrops= [node for node in nodes if node.Class() == 'BackdropNode']
        [nodes.remove(node) for node in backdrops]
        print(('nodes', nodes))
        print(('backdrops', backdrops))
        if len(nodes) == 1 and not backdrops:
            #1 node, no backdrops: choose all the other nodes and scale around that!
            #(if backdrops, scale those too)
            centerX, centerY= centerPos(nodes[0]) 
            nodes= nuke.allNodes()
            nodes.remove(nuke.selectedNode())
            #separate nodes into 2 lists: nodes and backdrops
            backdrops= [node for node in nodes if node.Class() == 'BackdropNode']
            [nodes.remove(node) for node in backdrops]
        if backdrops or nodes: #because sometimes we don't have anything
            #scale the selected nodes and backdrops
            if centerX == None and centerY == None:
                #if we don't have it, find centre points to scale around
                #if scaleX and scaleY:
                #    centerX, centerY= medianXY([centerPos(node) for node in nodes] )
                #else:
                if scaleX != 1:
                    try:
                        centerX= median_low([center_x(node) for node in nodes] )
                    except:
                        centerX= median([center_x(backdrop) for backdrop in backdrops] )
                     
                if scaleY != 1:
                    try:
                        centerY= median_low([center_y(node) for node in nodes] )
                    except:
                        centerY= median([center_y(backdrop) for backdrop in backdrops] )
            #print 'scale x',scaleX, 
            #print 'scale y',scaleY
            #print 'center x', centerX,
            #print 'center y', centerY
            #print [center_x(node) for node in nodes]


            # SCALE NODES 
            for node in nodes:
                if scaleX != 1:
                    #work out scale
                    deltaX= (center_x(node)- centerX)* scaleX
                    #if abs(deltaX)> minmove:
                    node.setXpos(int( centerX+ deltaX- node.screenWidth()/ 2.0))
                    #print "Scaling %d nodes %.1f around x=%d" % (len(nodes), scaleX, centerX)
                if scaleY != 1:
                    deltaY= (center_y(node)- centerY )* scaleY
                    #if abs(deltaY)> minmove:
                    node.setYpos( int(centerY+ deltaY- node.screenHeight()/ 2.0))
                    #print "Scaling %d nodes %.1f around y=%d" % (len(nodes), scaleY, centerY)

            for backdrop in backdrops:
                print((backdrop['label'].value()))
                #scale the four corners 
                if scaleX != 1:
                    deltaX= (backdrop.xpos()- centerX)* scaleX
                    deltaXw= (backdrop.xpos()+ backdrop.screenWidth()- centerX)* scaleX

                    #deltaX= (center_x(backdrop)- centerX )* scaleX
                    #print 'deltax=',deltaX
                    #backdrop.setXpos(int( centerX+ deltaX- backdrop.screenWidth()/ 2.0))
                    backdrop.setXpos(int( deltaX+ centerX))
                    #backdrop.setXpos(int(centerX+ deltaX- backdrop.screenWidth()/ 2.0))
                    #scale backdrop size
                    backdrop['bdwidth'].setValue(int(    deltaXw+ centerX- backdrop.xpos()    ))
            
                if scaleY != 1:
                    #deltaY= (center_y(backdrop)- centerY )* scaleY
                    #backdrop.setYpos( int(centerY+ deltaY- backdrop.screenHeight()/ 2.0))
                    #backdrop['bdheight'].setValue(backdrop.screenHeight()* scaleY)
                    deltaY= (backdrop.ypos()- centerY)* scaleY
                    deltaYw= (backdrop.ypos()+ backdrop.screenHeight()- centerY)* scaleY

                    backdrop.setYpos(int( deltaY)+ centerY)
                    backdrop['bdheight'].setValue(int(    deltaYw+ centerY- backdrop.ypos()   ))
            '''
            for backdrop, nodes in backdrops.items():
                #print backdrop.name(), nodes
                if nodes:
                    #scale backdrops to still cover nodes (which have already been scaled)
                    backdrop_sd.resize_bd(backdrop, selNodes= nodes)
                else:
                    #SCALE EMPTY BACKDROPS
                    if scaleX != 1:
                        #deltaX= ((backdrop.xpos()+ backdrop.screenWidth()/ 2.0)- centerX)* scaleX
                        deltaX=  (center_x(backdrop)- centerX )* scaleX
                        #print 'deltax=',deltaX
                        #backdrop.setXpos(int( centerX+ deltaX- backdrop.screenWidth()/ 2.0))
                        #backdrop.setXpos(int( (backdrop.xpos()-centerX)* deltaX)+ backdrop.xpos())
                        backdrop.setXpos(int(centerX+ deltaX- backdrop.screenWidth()/ 2.0))
                        #scale backdrop size
                        backdrop['bdwidth'].setValue(backdrop.screenWidth()* scaleX)
                
                    if scaleY != 1:
                        deltaY= (center_y(backdrop)- centerY )* scaleY
                        backdrop.setYpos( int(centerY+ deltaY- backdrop.screenHeight()/ 2.0))
                        backdrop['bdheight'].setValue(backdrop.screenHeight()* scaleY)'''

#TRANSLATE
# to do  - keep on backdrops 
'''def translate_nodes_up(nodes= nuke.selectedNodes()):
    import backdrop_sd
    if nodes:
        #make dir of all backdrops and nodes on each
        backdrops= {backdrop: backdrop_sd.nodes_in_backdrop(backdrop) for backdrop in nuke.allNodes('BackdropNode')}
        #print 'backdrops', backdrops
        #remove backdrops from selection
        [nodes.remove(backdrop) for backdrop in backdrops.keys() if backdrop in nodes]
    
    #move nodes:
    [node.setYpos(int(node.ypos()- nuke.toNode("preferences")["GridHeight"].value())) for node in nodes]
    
    #move backdrops


    for backdrop, nodes_on_backdrop in backdrops.items():
        #print backdrop.name(), nodes
        #if 
        if nodes_on_backdrop:
            #scale backdrops to still cover nodes (which have already been moved)
            backdrop_sd.resize_bd(backdrop, selNodes= nodes)
        else:
            #MOVE EMPTY BACKDROPS
            backdrop.setYpos(int(backdrop.ypos()- nuke.toNode("preferences")["GridHeight"].value())) '''

def translate_nodes_up(nodes):
    [node.setYpos(int(node.ypos()- nuke.toNode("preferences")["GridHeight"].value())) for node in nodes]

def translate_nodes_down(nodes):
    [node.setYpos(int(node.ypos()+ nuke.toNode("preferences")["GridHeight"].value())) for node in nodes]

def translate_nodes_left(nodes):
    [node.setXpos(int(node.xpos()- nuke.toNode("preferences")["GridWidth"].value())) for node in nodes]

def translate_nodes_right(nodes):
    [node.setXpos(int(node.xpos()+ nuke.toNode("preferences")["GridWidth"].value())) for node in nodes]



#ROTATE 
#todo: centre rotation around median node
#add to nodes-> transform/rotate/scale menu
#add an arbitrary rotate
#keep on backdrops etc

'''
def rotate_nodes_clockwise(nodes= nuke.selectedNodes()):
    for node in nuke.selectedNodes():
        node.setXYpos(int(node['ypos'].value()), int(node['xpos'].value()))

def rotate_nodes_anticlockwise(nodes= nuke.selectedNodes()):
    for node in nuke.selectedNodes():
        node.setXYpos(int(node['ypos'].value()), int(-node['xpos'].value()))
''' 
def rotatePoint(centerPoint, point, angle):
    """Rotates a point around another centerPoint. Angle is in degrees.
    Rotation is counter-clockwise"""
    import math
    angle= math.radians(angle)
    temp_point= point[0]- centerPoint[0], point[1]- centerPoint[1]
    temp_point= (temp_point[0]* math.cos(angle)- temp_point[1]* math.sin(angle), temp_point[0]* math.sin(angle)+ temp_point[1]* math.cos(angle))
    temp_point= temp_point[0]+ centerPoint[0], temp_point[1]+ centerPoint[1]
    return temp_point

def rotatePoint90(centerPoint, point):
    #Rotates a point 90 degrees around centerPoint.
    return centerPoint[0]- point[1]+ centerPoint[1], point[0]- centerPoint[0]+ centerPoint[1]

def rotatePointMinus90(centerPoint, point):
    #Rotates a point 90 degrees around centerPoint.
    return point[1]- centerPoint[1] + centerPoint[0], -point[0]+ centerPoint[0]+ centerPoint[1]



#print rotatePoint((1,1),(2,2),45)      
def rotate_nodes_clockwise(nodes):
    centerX= mean([center_x(node) for node in nodes])
    centerY= mean([center_y(node) for node in nodes])
    for node in nuke.selectedNodes():
        a= rotatePoint90((centerX, centerY), (node['xpos'].value(), node['ypos'].value()) ) 
        node.setXYpos(    int(a[0]), int(a[1])  )   
        #node.setXYpos(int(node['ypos'].value()+ centerX- centerY), int(node['xpos'].value()+ centerY- centerX))

def rotate_nodes_anticlockwise(nodes):
    centerX= mean([center_x(node) for node in nodes])
    centerY= mean([center_y(node) for node in nodes])
    for node in nuke.selectedNodes():
        a=rotatePointMinus90((centerX, centerY), (node['xpos'].value(), node['ypos'].value()) ) 
        node.setXYpos(    int(a[0]), int(a[1])  ) 
        #node.setXYpos(int(node['ypos'].value())+ centerX- centerY, int(-node['xpos'].value()+ centerY- centerX))

def rotate_nodes_arbitrary(nodes, angle= None, centerX= None, centerY= None ):
    if not nodes:
        nodes= nuke.allNodes()
    #get angle
    if angle == None:
        #ask user for an angle
        bkDefault= -26.5   #reverse the problem where multiple read nodes come in at an angle       
        bkDisplay= bkDefault
        question= 'Angle:'
        panel = nuke.Panel("Rotate Nodes by Sean Danischevsky")
        panel.setWidth(300)
        panel.addSingleLineInput(question, bkDisplay)
        if panel.show(): #display panel. Input from user.
            if panel.value(question) == "" or panel.value(question) == bkDisplay: 
                #user writes nothing
                angle= float(bkDefault)
            else:
                angle= float(panel.value(question))
        else: #user cancels
            raise Exception('User cancelled')
            return "User cancelled"
    print(angle)
    centerX= mean([center_x(node) for node in nodes])
    centerY= mean([center_y(node) for node in nodes])
    for node in nodes:
        a= rotatePoint((centerX, centerY), (node['xpos'].value(), node['ypos'].value()), angle) 
        node.setXYpos(    int(a[0]), int(a[1])  ) 