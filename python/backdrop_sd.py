################################
#backdrop_sd
#by Sean Danischevsky 2010,2012
#Automatically puts a backdrop behind the selected nodes.
#Backdrop will fit all the select nodes, with room at the top for text in a large font.
#Uses Mona lisa colour palette as default. To set a color collection for your show,
#put a file called nuke_colors.txt somewhere in the NUKE_PATH for your show.
#For personal colours, use  ~/.nuke/nuke_colors.txt
#The file should contain a line of HTML style hex colors, letters in CAPS, separated by commas, e.g. 
#A60D0D,5AA60D,0DA60D,0D5AA6,0D0DA6,A60D5A
#It ignores lines starting with a hash '#'
#It takes only the first valid line in the file.
#You can get colorschemes from websites like:
#http://www.colorhunter.com
#http://www.colorcombos.com and
#http://www.colorjack.com
#
#Another way to get a collection is to select some nodes in a script and run 
#'scan_nodes_for_collection()' in Nuke's Script Editor. 
#This will create backdrop nodes from this collection and print the 
#text you need.

import nuke, random, string, math, datetime, os
#import sys
#sys.path.append("/data/apps/python/modules/cent5_x86_64_py26/SciPy/0.10.1")
#import scipy
#import numpy

def is_safe_path(file_path):
    """Validate that a file path is safe to read from"""
    if not file_path or not isinstance(file_path, str):
        return False
    
    # Normalize the path
    try:
        normalized_path = os.path.normpath(file_path)
    except:
        return False
    
    # Check for path traversal attempts
    if '..' in normalized_path:
        return False
    
    # Check if the file exists and is readable
    try:
        return os.path.isfile(normalized_path) and os.access(normalized_path, os.R_OK)
    except (OSError, IOError):
        return False

def get_colors():
    #Use mona lisa colour palette as default:
    #collection =[3604397313, 4292418049, 4287367937, 3944521217, 4278190081, 1577058305, 3220521473, 2277965825, 9502721, 944177153, 2800939521, 12558593, 26113, 1494410753]  
    #collection =[3604397313]
    #collection = [944177153, 12558593, 2800939521, 1949176319, 3220521473, 2277965825, 4287367937, 1903281664, 4292418049, 3604397313, 3435954431, 2391685120, 640050943, 2356888063, 2391504127, 1228738559, 742019071, 1350340351]
    #mona lisa colours:
    #defaultCollection= [538588160, 707742976, 1145131264, 1853584384, 1652190464, 1198678272, 1080508416, 1533429760, 1464738560, 2403607296, 3547818496, 3095865856, 2878348800, 3013637632, 2997909760, 3015540992, 3048453632, 2242495232]
    defaultCollection= [538588160, 1145131264, 1601077504, 1853584384, 1652190464, 1198678272, 1080508416, 1533429760, 1194403328, 2403607296, 3547818496, 3095865856, 2878348800, 3013637632, 3048453632, 2242495232]
    #2a2f4d00,6e7b7400,40674000,47726100,b2b07900,b3bd8100,af713000,5b664800,b3a07600,44415100,f1cd6c00,81926600,8f442300,201a3400,fedc8a00,ab901e00,574e2300,627a6d00
    #print 'searching nuke.pluginPath for nuke_colors.txt:\n', nuke.pluginPath()
    for dir in nuke.pluginPath():
        fileName = os.path.join(dir, "nuke_colors.txt")
        #print 'looking for',fileName
        if os.path.exists(fileName) and is_safe_path(fileName):
            print(('reading',fileName))
            try:
                with open(fileName, 'r') as file:
                    lines = file.readlines()
                lines = [line.strip() for line in lines]
                lines = [line for line in lines if len(line) > 0 and line[0] != '#']
                if len(lines) < 1:
                    raise Exception('Empty nuke_colors.txt')     
                    return defaultCollection
                lines = [line.split(',') for line in lines]
                hexes=[]
                # in future, would be nice to have many lines and choose scheme at random,
                #then build on that choice. But for now take first line:
                for hex in lines[0]:
                    hexes.append(  hex_to_RGBInt(hex)  )        
                return hexes
            except (IOError, OSError, Exception) as e:
                print(f"Error reading {fileName}: {e}")
                continue
        else:
            #print "Put a nuke_colors.txt file in your NUKE_PATH. Couldn't find such a file in", nuke.pluginPath()
            #raise Exception('No nuke_colors.txt')
            continue
    return defaultCollection

def scan_nodes_for_collection(nodes):
    #scan tile color of nodes and print to terminal the collection as RGBInt
    #(to be pasted into the collection file).
    collection = []
    for node in nodes:
        node_color = node['tile_color'].value()
        if node_color != 0 and node_color not in collection:
            collection.append(node_color)
    show_collection_as_backdrops(collection)
    return

def clamp(value, min, max):
        return (min if value < min else (max if value > max else value))

def hex_to_RGBInt(hex):
          hex = string.upper(hex.strip( '#' ))
          rr = int( hex[0:2], 16 ) / 255.0
          gg = int( hex[2:4], 16 ) / 255.0
          bb = int( hex[4:6], 16 ) / 255.0
          rr = clamp (rr, 0, 1)
          gg = clamp (gg, 0, 1)
          bb = clamp (bb, 0, 1)
          return int('%02x%02x%02x%02x' % (rr* 255, gg* 255, bb* 255, 1), 16)

def tuple_to_rgba_int(r, g, b, a):
    return int('%02x%02x%02x%02x' % (clamp(r, 0, 1)* 255, clamp(g, 0, 1)* 255, clamp(b, 0, 1)* 255, clamp(a, 0, 1)* 255), 16)

def rgb_int_to_rgb(intcol, alphaOut= 0):
    #turns nuke tile color into rgb tuple
    #by Sean Danischevsky 2012
    tmp, alpha= divmod(intcol, 256)
    tmp, blue = divmod(tmp, 256)
    red, green= divmod(tmp, 256)
    if alphaOut:
        return red/ 255.0, green/ 255.0, blue/ 255.0, alpha/ 255.0
    else:
        return red/ 255.0, green/ 255.0, blue/ 255.0
'''
def closest(X, p, weights=0):
    #finds closest point in X to p. 
    #weights is a scale factor 
    if not weights:
        disp = X - p
    else:
        disp = X*weights - p*weights
    return X[numpy.argmin((disp*disp).sum(1))]
'''
def rename_bd(bd, label= None):
    if label != None:
        #don't ask
        #to do: make this more robust
        bkName= str(label)
    else:
        #ask user
        try:
            import pwd
            if pwd.getpwuid(os.getuid())[4]:
                username= pwd.getpwuid(os.getuid())[4]
            else:
                username= pwd.getpwuid(os.getuid())[0]
        except:
            username=os.getenv("USERNAME")
        bkDisplay= 'Label backdrop:' #display text
        now= datetime.datetime.now()   
        today= now.strftime("%d %B %Y, %H:%M")
        bkDefault= '%s\n%s'%(username,today)
        #Ask the user
        panel= nuke.Panel("Backdrop settings")
        panel.setWidth(220)
        panel.addSingleLineInput('Name:', bkDisplay)
        if panel.show(): 
            #display panel. Input from user.
            if panel.value('Name:') == "" or panel.value('Name:') == bkDisplay: 
                #user wrote nothing
                bkName = bkDefault
            else:
                bkName = panel.value('Name:')
        else: 
                raise Exception('User cancelled')
                return "User cancelled"
    
    #label the bd
    bd['label'].setValue(bkName)
    bd['note_font_size'].setValue(bd_font_size)
    return

def resize_bd(bd, selNodes= []):
    # Calculate bounds for the backdrop node.
    gw= nuke.toNode("preferences")["GridWidth"].value()
    #print 'gw',gw
    bd_sides=  gw/ 2
    gh= nuke.toNode("preferences")["GridHeight"].value()
    #print 'gh',gh
    bd_bottom= grid_max((bd_font_size* 1.25), gh)
    bd_top= bd_bottom* 3
    #print 'bd_sides, bd_top, bd_bottom',bd_sides, bd_top, bd_bottom
    if selNodes:
        bdX= min([node.xpos() for node in selNodes])
        bdY= min([node.ypos() for node in selNodes])

        bdX-= bd_sides
        bdY-= bd_top
        bdX= grid_min(bdX, gw)
        bdY= grid_min(bdY, gh)

        bdW= max([node.xpos()+ node.screenWidth() for node in selNodes])- bdX
        bdH= max([node.ypos()+ node.screenHeight() for node in selNodes])- bdY 
        bdW+= bd_sides
        bdH+= bd_bottom

    else:
        bdX= bd.xpos()
        bdY= bd.ypos()
        bdX= grid_min(bdX, gw)
        bdY= grid_min(bdY, gh)
        bdW= bd['bdwidth'].value()
        bdH= bd['bdheight'].value()
    bdW = grid_max(bdW, gw* 2)
    bdH = grid_max(bdH, gh* 2)
    #Move if necessary:
    #print bd['xpos'].value(),bdX 
    #print bd['ypos'].value(),bdY
    #print bd['bdwidth'].value(),bdW 
    #print bd['bdheight'].value(),bdH
    if bd['xpos'].value() != bdX or bd['ypos'].value() != bdY or bd['bdwidth'].value() != bdW or bd['bdheight'].value() != bdH:
        bd['xpos'].setValue(bdX)
        bd['ypos'].setValue(bdY)
        bd['bdwidth'].setValue(bdW)
        bd['bdheight'].setValue(bdH)
        return 1
    else:
        return

def grid_max(inputValue, gridValue):
    #returns ceiling value
    return int(math.ceil(inputValue/ float(gridValue))* gridValue)

def grid_min(inputValue, gridValue):
    #returns floor value
    return (inputValue// gridValue)* gridValue

######## SET THE DEFAULTS ########
# Expand backdrop border. Offsets for left, top, right and bottom:
bd_font_size= 42
collection= get_colors()
#print 'coll=', collection
#should really add this to a pane in preferences.

###############################################################
# BACKDROP REORDERING
#
#       select_backdrop_contents
#       nodeInBackdrop
#       nodes_in_backdrop
#       fix_backdrop_depth
###############################################################

def select_backdrop_contents(backdropNode):
    '''Select all nodes inside a backdrop.
    There is a built in method for this on Nuke6.3v5,
    but this is kept here to expand compatibility
    to earlier versions
    '''
    import nukescripts
    bx, by= backdropNode.xpos(), backdropNode.ypos()
    nukescripts.clear_selection_recursive()
    backdropNode.setSelected(True)
    nuke.nodeCopy(nukescripts.cut_paste_file())
    nuke.nodeDelete(popupOnError= False)
    nuke.nodePaste(nukescripts.cut_paste_file())
    nuke.selectedNode().setXYpos(bx, by)

def nodeIsInside (node, backdropNode): 
    """Returns true if node geometry is inside backdropNode otherwise returns false""" 
    if node!= backdropNode:
        topLeftNode = [node.xpos(), node.ypos()] 
        topLeftBackDrop = [backdropNode.xpos(), backdropNode.ypos()] 
        bottomRightNode = [node.xpos() + node.screenWidth(), node.ypos() + node.screenHeight()] 
        bottomRightBackdrop = [backdropNode.xpos() + backdropNode.screenWidth(), backdropNode.ypos() + backdropNode.screenHeight()] 

        topLeft = ( topLeftNode[0] >= topLeftBackDrop[0] ) and ( topLeftNode[1] >= topLeftBackDrop[1] ) 
        bottomRight = ( bottomRightNode[0] <= bottomRightBackdrop[0] ) and ( bottomRightNode[1] <= bottomRightBackdrop[1] ) 

        return topLeft and bottomRight

def nodes_in_backdrop(backdropNode):
    '''
    nodes_in_backdrop(backdropNode) -> bool
    
    Returns all nodes contained within the backdrop
    '''
    return [n for n in nuke.allNodes() if nodeIsInside(n, backdropNode)]

def fix_backdrop_depth():
    '''
    Layer smaller backdrops on top of bigger ones
    '''
    import nukescripts
    original_selection= nuke.selectedNodes()
    sel = nuke.selectedNodes('BackdropNode')
    all = nuke.allNodes('BackdropNode')
    all.sort(key= lambda x: x.screenHeight()* x.screenWidth(), reverse= True)
    try:
        [b.selectNodes() for b in all]
    except: # This will be used for Nuke versions below 6.3v5
        [select_backdrop_contents(b) for b in all]
    nukescripts.clear_selection_recursive()
    [i.setSelected(1) for i in original_selection]

####################
def make_backdrop(selNodes, label= None):
    #print selNodes
    gw= nuke.toNode("preferences")["GridWidth"].value()
    #print 'gw',gw
    bd_sides=  gw/ 2
    gh = nuke.toNode("preferences")["GridHeight"].value()
    #print 'gh',gh
    bd_bottom= grid_max((bd_font_size* 1.25),gh)
    bd_top= bd_bottom* 3
    #print 'bd_sides, bd_top, bd_bottom',bd_sides, bd_top, bd_bottom
    #selNodes = nuke.selectedNodes()
    #Resize/recolour/create backdrop nodes
    
    if not selNodes:
        #create the node
        bd= nuke.createNode("BackdropNode") 
        tile_color= random.choice(collection)
        bd['tile_color'].setValue(tile_color)
        bd['bdwidth'].setValue(grid_max((bd_font_size* 6),gw* 2))
        bd['bdheight'].setValue(grid_max((bd_font_size* 4),gh* 2))
        #label and resize
        try:
            rename_bd(bd, label)
            resize_bd(bd)
        except:
            nuke.delete(bd)
        #always fix the depth for all BD nodes
        fix_backdrop_depth()
        return bd


    #count backdrop nodes
    #bdNodes=nuke.selectedNodes("BackdropNode")
    bdNodes= [node for node in selNodes if node.Class() == "BackdropNode"]


    #only nodes selected (no backdrop nodes) - create backdrop node around nodes
    if not bdNodes:
        #create the bd 
        bd = nuke.createNode("BackdropNode")

        #resize the bd
        resize_bd(bd, selNodes)

        #color the bd
        bd['tile_color'].setValue (random.choice(collection))

        #label the bd
        try:
          rename_bd(bd, label)
          for node in selNodes:
              node['selected'].setValue(True)
        except:
          nuke.delete(bd)
        #always fix the depth for all BD nodes
        fix_backdrop_depth()
        return bd


    #just one backdrop selected?
    if len(bdNodes) == 1:
        #select the bd and remove it from list
        bd= bdNodes[0]
        selNodes.remove(bd)
 
        #if unlabelled, label bd  
        if not bd['label'].value():
            try:
                rename_bd(bd, label)
            except:
                print('Leaving backdrop node name blank.')
        
        #try to resize to fit
        if resize_bd(bd, selNodes):
            #Node changed size, so break
            #always fix the depth for all BD nodes
            fix_backdrop_depth()
            return
        
        #if in collection, cycle color
        if bd['tile_color'].value() in collection:
            newcol=  (collection.index(bd['tile_color'].value())+ 1)% len(collection)   
            bd['tile_color'].setValue (collection[newcol])
        else: 
            #pick random
            #bd['tile_color'].setValue (random.choice(collection))
            #pick nearest
            reformat_backdrops(bd, fix_size= False, fix_fonts= False, fix_color= 'nearest')

        #always fix the depth for all BD nodes
        fix_backdrop_depth()
        return

    #what I'd like to do is:
    #more than one BD selected, and all nodes on bacdrop: reformat all selected. If nothing to do, add big backdrop behind
    #if there are nodes not on backdrop, put all backdrops on a big backdrop
    #but for now....
    elif len(bdNodes)> 1:
        #reformatted= reformat_backdrops(bdNodes, fix_size= True, fix_fonts= False, fix_color= 'nearest')
        #if not reformatted:
        #    #there was no reformattiing to do, so make a big backdrop behind selected nodes and backdrops
        return reformat_backdrops(bdNodes, fix_size= True, fix_fonts= False, fix_color= 'nearest')


def show_collection_as_backdrops(collection= collection):
    #create a palette of backdrop nodes using the current collection
    #or give a collection of RGBInt numbers as a list, e.g.
    #show_collection_as_backdrops([538588160, 1652190464, 1194403328, 2878348800])
    print(('collection=', collection))
    xlen= int(math.sqrt(len(collection)))
    size= 100
    #add max x of all existing nodes so we have space
    maxx= max([(node.xpos()+ node.screenWidth()) for node in nuke.allNodes()]) 
    maxy= max([(node.ypos()+ node.screenHeight()) for node in nuke.allNodes()]) 
    #ask if we want to write out the file. what path,(show possibles), right name ( nuke_colors.txt )
    #label them with the hex and rgb
    for i, rgb in enumerate(collection):
         bd= nuke.nodes.BackdropNode(xpos= (i// xlen)* size+ maxx, ypos= (i% xlen)* size+ maxy, tile_color= rgb, bdwidth= size, bdheight= size, label= rgb)


def reformat_backdrops(nodes, fix_size= None, fix_fonts= None, fix_color= None):
    #reformat selected backdrop nodes to my preferred scheme
    #if no nodes selected, 
    #gw= nuke.toNode("preferences")["GridWidth"].value()
    #print 'gw',gw
    #bd_sides=  gw/ 2
    #gh= nuke.toNode("preferences")["GridHeight"].value()
    #print 'gh',gh
    #bd_bottom= grid_max((bd_font_size* 1.25), gh)
    #bd_top= bd_bottom* 3
    #print 'bd_sides, bd_top, bd_bottom',bd_sides, bd_top, bd_bottom
    #print 'collection=',collection

    #work on backdrop nodes only
    nodes= [node for node in nodes if node.Class() == "BackdropNode"]

    #if no nodes selected, select all
    if not nodes:
        nodes= nuke.allNodes("BackdropNode")

    if nodes:
        if fix_size == None or fix_fonts == None or fix_color == None:
            #ask user
            panel= nuke.Panel("Reformat Backdrop Nodes")
            #future: add 'fix font size/style' options
            panel.addBooleanCheckBox('Fix size', True)
            panel.addBooleanCheckBox('Fix fonts', True)
            panel.addEnumerationPulldown('Color', "nearest random don't\ fix")
            if panel.show():
                fix_size= panel.value('Fix size')
                fix_fonts= panel.value('Fix fonts')
                fix_color= panel.value('Color')
            else:
                #user cancels
                raise Exception('User cancelled')
                #always fix the depth for all BD nodes
                fix_backdrop_depth()
                return "User cancelled"

        #fix size
        if fix_size:
            #get non-bd nodes that sit entirely inside each bd
            '''a= nuke.allNodes()
            b= nuke.allNodes("BackdropNode")
            nonbd= set(a)- set(b)
            for bd in nodes:
                #get the size of the bd node
                bdminx= bd.xpos()
                bdminy= bd.ypos()
                bdmaxx= bdminx+ bd['bdwidth'].value()
                bdmaxy= bdminy+ bd['bdheight'].value()
                #print bdminx,bdminy,bdmaxx,bdmaxy
                selNodes= []                   
                for i in nonbd:
                    #test each node
                    if (i.xpos() >= bdminx) and (i.ypos() >= bdminy) and (i.xpos() + i.screenWidth() <= bdmaxx) and  (i.ypos() + i.screenWidth() <= bdmaxy):
                        selNodes.append(i)'''
            [resize_bd(bd, nodes_in_backdrop(bd)) for bd in nodes]
        
        #fix fonts?
        if fix_fonts:
            for bd in nodes:
                bd['note_font_size'].setValue(bd_font_size)
                bd['note_font'].setValue(nuke.toNode("preferences")["UIFont"].value())
        
        #fix colours?
        if fix_color == 'random':
            for bd in nodes:
                if bd['tile_color'].value() not in collection:
                    bd['tile_color'].setValue(random.choice(collection))

        elif fix_color == 'nearest':
                if bd['tile_color'].value() not in collection:
                    for bd in nodes:
                        #convert collection to rgb and store distance
                        #using weighting: rr*.3+gg*.59+bb*.11
                        tr, tg, tb= rgb_int_to_rgb(bd['tile_color'].value())
                        cube= {}
                        for i, col in enumerate(collection):
                            sr, sg, sb= rgb_int_to_rgb(col)
                            dist= pow((sr- tr), 2)* .3+ pow((sg- tg), 2)* .59+ pow((sb- tb), 2)* .11
                            cube[col]= dist
                        #find nearest colour
                        mindist= min(cube, key= cube.get)
                        #print mindist
                        bd['tile_color'].setValue(mindist)
        #always fix the depth, for all BD nodes
        fix_backdrop_depth()
        return


def autocolor_bd():
    #color backdrops automatically based on first line
    #sean danischevsky 2014
    #we're changing the label, and the gl_color is default 
    #to *not* change the color, set the gl_color to anything else:
    if nuke.thisKnob().name() == "label" and nuke.thisNode()['gl_color'].getValue() == nuke.thisNode()['gl_color'].defaultValue():
        collection= get_colors()
        #convert label to lower case, use only first line
        myHash= hash(nuke.thisNode().knob('label').value().lower().split("\n")[0])
        collectionIndex= myHash% len(collection)
        nuke.thisNode().knob('tile_color').setValue(collection[collectionIndex])
        return




