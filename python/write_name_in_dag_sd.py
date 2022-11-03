###########################################
# by Sean Danschevsky 2010, updated in 2012, 2017, 2022
# write a message or make an image in the DAG,
# made from dots or Backdrop Nodes
###########################################

import nuke

def clamp(value, min, max):
        return (min if value < min else (max if value > max else value))

def rgbaInt_to_tuple(rgbint):
    return (rgbint //256/256/256%256/256.0, rgbint // 256 // 256 % 256/256.0, rgbint // 256 % 256/256.0, rgbint % 256/256.0)

def tuple2rgba_int(r,g,b,a):
    return int('%02x%02x%02x%02x' % (int(clamp(r,0,1)*255), int(clamp(g,0,1)*255), int(clamp(b,0,1)*255), int(clamp(a,0,1)*255)),16)

def hex_to_RGBInt(hex):
          hex = string.upper(hex.strip( '#' ))
          rr = int( hex[0:2], 16 ) / 255.0
          gg = int( hex[2:4], 16 ) / 255.0
          bb = int( hex[4:6], 16 ) / 255.0
          rr = clamp (rr,0,1)
          gg = clamp (gg,0,1)
          bb = clamp (bb,0,1)
          return int('%02x%02x%02x%02x' % (rr*255,gg*255,bb*255,1),16)

def write_name_or_image_in_dag():
    nodes= nuke.selectedNodes()
    if len(nodes)> 1:
        nuke.message ("Select a single node to create it in the DAG,\n(or no nodes to write a message).")
        return
    elif len(nodes) == 1:
        node= nodes[0]
        if 'rgba.red' in node.channels():
            write_image_in_dag(node)
        else:
            nuke.message ("Select a node with an RGB ouput!") 
    else:
        #no image selected: write a message instead
        write_name_in_dag()
    return



def write_image_in_dag(node):
    import math
    panel = nuke.Panel("Create image in the DAG")
    panel.setWidth(300)
    panel.addSingleLineInput("Maximum samples", 100)
    hexBool= None
    panel.addBooleanCheckBox("Hexagonal style", hexBool)
    nodestyle= "Dot Backdrop"
    panel.addEnumerationPulldown("Node style", nodestyle) 
    keepNodesBool= False
    panel.addBooleanCheckBox("Keep reformat nodes", keepNodesBool)

    #display panel. Input from user.
    if not panel.show():
            #user cancels
            raise Exception('User cancelled')
            return "User cancelled"
    max_size= int(panel.value("Maximum samples"))
    hexagonal= panel.value("Hexagonal style")
    keep_nodes= panel.value("Keep reformat nodes")
    nodeStyle= panel.value("Node style")

    #create reformat nodes
    createdNodes=[]
    re= nuke.nodes.Reformat()
    createdNodes.append(re)
    re.setInput(0,node)
    re['type'].setValue('scale')
    scalevalue= float(node.width()* node.height()   ) 
    print(('max_size=', max_size, 'area=',scalevalue, float(math.sqrt((max_size)/ scalevalue))))
    re['scale'].setValue(min (1, float(math.sqrt((max_size)/ scalevalue))))
    cs= nuke.nodes.Colorspace()
    createdNodes.append(cs)
    cs.setInput(0, re)
    cs['colorspace_out'].setValue("sRGB")
    sn= cs
    #print 'here'


    #add max x of all existing nodes so we have space
    maxx= max([(node.xpos()+ node.screenWidth()) for node in nuke.allNodes()]) 
    maxy= max([(node.ypos()+ node.screenHeight()) for node in nuke.allNodes()]) 
    if nodeStyle == 'Backdrop':
        size= nuke.toNode("preferences")['dot_node_scale'].value()* 20
    else:
        size= nuke.toNode("preferences")['dot_node_scale'].value()* 10



    task= nuke.ProgressTask("Painting a picture")
    for yy in range(sn.height()):
        for xx in range(sn.width()):
            if task.isCancelled():
                break
            # UPDATE PROGRESS BAR
            task.setProgress( int( float(yy) / float(sn.height())*100) )
            red= sn.sample('red',xx,yy)
            green= sn.sample('green',xx,yy)
            blue= sn.sample('blue',xx,yy)
            hexColor=tuple2rgba_int(red,green,blue,0)
            if hexagonal:
                if nodeStyle == 'Backdrop':
                    dott = nuke.nodes.BackdropNode(xpos= maxx+ math.fmod(yy,2)*(size/2)+(xx*size),ypos=maxy-yy*size,bdwidth=size, bdheight=size,tile_color=hexColor)
                else:
                    dott = nuke.nodes.Dot         (xpos= maxx+ math.fmod(yy,2)*(size/2)+(xx*size),ypos=maxy-yy*size, hide_input=1,tile_color=hexColor)
            else:
                if nodeStyle == 'Backdrop':
                    dott = nuke.nodes.BackdropNode(xpos= maxx+ (size/ 2)+ (xx* size), ypos= maxy-yy*size, bdwidth=size, bdheight=size,tile_color=hexColor)
                else:
                    dott = nuke.nodes.Dot         (xpos= maxx+ (size/ 2)+ (xx* size), ypos= maxy-yy*size, hide_input=1,tile_color=hexColor)
    del(task)


    if not keep_nodes:
        for node in createdNodes:
            nuke.delete(node)
    return



def write_name_in_dag():
    import math, os
    try:
        import pwd
        username= pwd.getpwuid(os.getuid())[4]
    except:
        username= os.getenv("USERNAME")

    #Ask the user what to write
    bkDisplay= username #display text
    bkDefault= username #what to write if user just presses return
    panel= nuke.Panel("Message to print on the DAG")
    panel.setWidth(300)
    panel.addSingleLineInput('Message', bkDisplay)
    panel.addSingleLineInput('Size',20)
    hexBool= None
    panel.addBooleanCheckBox("Hexagonal style", hexBool)
    aliasBool= True
    panel.addBooleanCheckBox("Anti-aliasing", aliasBool)
    keepNodesBool= False
    nodestyle= "Dot Backdrop"
    panel.addEnumerationPulldown("Node style", nodestyle) 
    panel.addBooleanCheckBox("Keep text nodes", keepNodesBool)

    #display panel. Input from user.
    if panel.show():
        bkName = panel.value('Message')
        progressBarName= "Writing %s" % (bkName)
        if not bkName or bkName == bkDisplay: 
            #user wrote nothing
            bkName= bkDefault
            progressBarName= "%s. What a lovely name!" % (bkName)
    else: 
            #user cancels
            raise Exception('User cancelled')
            return "User cancelled"
    text_size= int(panel.value("Size"))
    hexagonal= panel.value("Hexagonal style")
    aliasing= panel.value("Anti-aliasing")
    keep_nodes= panel.value("Keep text nodes")
    nodeStyle= panel.value("Node style")

    #create text nodes
    createdNodes= []
    tt= nuke.createNode("Text2")#do it this way to set good font name!
    createdNodes.append(tt)
    tt.setInput(0, None)
    tt['message'].setValue(bkName)
    #tt['size'].setValue(text_size)
    tt['cliptype'].setValue("no clip")
    sn= nuke.nodes.Crop()
    createdNodes.append(sn)
    sn.setInput(0, tt)
    sn['box'].setExpression('input.bbox.x', 0)
    sn['box'].setExpression('input.bbox.y', 1)
    sn['box'].setExpression('input.bbox.x+ input.bbox.width', 2)
    sn['box'].setExpression('input.bbox.y+ input.bbox.height', 3)
    sn['reformat'].setValue("True")

    #add max x of all existing nodes so we have space
    maxx = max([(node.xpos()+ node.screenWidth()) for node in nuke.allNodes()]) 
    maxy = max([(node.ypos()+ node.screenHeight()) for node in nuke.allNodes()]) 
    if nodeStyle == 'Backdrop':
        size= nuke.toNode("preferences")['dot_node_scale'].value()* 20
    else:
        size= nuke.toNode("preferences")['dot_node_scale'].value()* 10
    bg= rgbaInt_to_tuple(     nuke.toNode("preferences")['DAGBackColor'].value()    )


    #set task bar 
    task= nuke.ProgressTask(progressBarName)
    #no_of_pixels= sn.height()* sn.width()
    #count= 0
    #create the nodes
    for yy in range(sn.height()):
        for xx in range(sn.width()):
            if task.isCancelled():
                break
            # UPDATE PROGRESS BAR
            #task.setMessage( 'Processing directory %s' % walkPath )
            #task.setProgress( int( float(xx*yy) / float(no_of_pixels)*100) )
            task.setProgress( int( float(yy) / float(sn.height())*100) )
            red= sn.sample('red', xx, yy)
            if (aliasing and red> bg[0]) or (not aliasing and red> .5):
                if hexagonal:
                    if nodeStyle == 'Backdrop':
                        dott= nuke.nodes.BackdropNode(xpos= maxx+ math.fmod(yy, 2)* (size/ 2)+ (xx* size), ypos= maxy- yy* size, bdwidth= size, bdheight= size)
                    else:
                        dott= nuke.nodes.Dot         (xpos= maxx+ math.fmod(yy, 2)* (size/ 2)+ (xx* size), ypos= maxy- yy* size, hide_input= 1)
                else:
                    if nodeStyle == 'Backdrop':
                        dott= nuke.nodes.BackdropNode(xpos= maxx+ (size/ 2)+ (xx* size), ypos= maxy- yy* size, bdwidth= size, bdheight= size)
                    else:
                        dott= nuke.nodes.Dot         (xpos= maxx+ (size/ 2)+ (xx* size), ypos= maxy- yy* size, hide_input= 1)
                if aliasing:
                    #colour the nodes (greyscale)
                    hexColor= tuple2rgba_int(red, red, red, 0)
                    dott['tile_color'].setValue(hexColor)
    del(task)

    if not keep_nodes:
        for node in createdNodes:
            nuke.delete(node)
    return

###########################
#runs when testing:
if __name__ == "__main__":
    write_name_or_image_in_dag()
