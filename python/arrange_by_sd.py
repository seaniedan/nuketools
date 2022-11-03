import nuke
import os
import copy

def arrange_by(nodes, sortKey= None, sortReverse= False, sortArrange= 'horizontal', sortSnap= True, sortDiscrete= False):
    
    ##########################
    ##############
    #arrange by...
    #by Sean Danischevsky 2012, 2016, 2017
    #
    #
    #
    #needs at least 2 nuke nodes as input
    #arranges nodes based on a given key, or
    #whatever it can find that is different
    #e.g. knobs, file metadata/extensions.
    #
    #
    #a function to determine whether the values are 'discrete'
    #i.e. if a file path, use the uppermost directory
    #and a function to label the discrete result
    #
    #
    #need to fix sortSnap - i'd prefer it to be True
    #sortDiscrete: would like to add functions 'True', 'Guess', and integer = split into even groups of that many?
    #
    #to do:
    #exr/type is broken -
    #blacklist certain knobs, e.g. xpos - we have a custom function for x position -
    #remove ordered dic: sort dics keys then add together in *list*
    #e.g. print sorted(dict.keys() key = lambda x: dict[x][2])
    
    #add basename? and 'extension' to the 'always' list!
    #rename "seperate discrete values'->'group'.
    #add option to backdrop based on the groups.
    #Add pyqt? to enable menus, e.g. sort by image/etc...
    #add imagemagick options. Only show what has been found.
    #Add option to move nodes above with the laid out nodes. Cheap way: select how many nodes above. Better way: checkbox to include nodes above/below which aren't shared by other nodes in the selection for layout.
    #Add option to layout only adjusting x or y. (e.g. for multiple write nodes, you want to keep them below their scripts, but see if any are the 'same'.
    #Add submenus or at least dividers eg. 'bbox/... options (top, left, centre, area)...or at least dividers. Use http://www.thefoundry.co.uk/products/nuke/developers/90/pythondevguide/custom_panels.html#pythonpanel-ref-label
    #Add 'sort by directory' - highest level different directory. e.g. would seperate /mnt/projects/aojd/.... and /mnt/projects/elements/... backdrop labels would therefore be 'elements' and 'aojd'. Same as sort by file but for 'group' it takes the highest level directory that's different and groups by that:
    #highest= os.path.commonprefix(files)
    #highest.split(os.sep)[-2]    
    
    #if arranging in squares etc, each 'discrete' group is a separate square.
    
    #add special functions for colour chip knobs, e.g. sort by luma/redness etc.
    #do proper snapping to grid
    #be nice to work out from all nodes in a script, what the best fit grid would be
    #make it faster: use first knobs to define what we look for in others and break like metadata?
    #add a 'sort in place' arrangement: list all xy positions and just rearrange using those
    #i.e. working left to right, top to bottom
    #add auto suggestions = if x minmax is less than y minmax, suggest arrange by y
    #default should be to arrange by xpos.
    #remove name and x,y pos from knob list
    #the SMART way to do KNOBS is to create a dir of knobs,lambda from the getgo.
    #maybe get knobs and class... and if it's a certain class, use certain lambda.
    #then run through the knobs and metas and say, if this one exists, add this one(width and height? add size)
    #THEN evaluate to see if it's worth adding to the GUI.
    #what would be SO COOL would be to add confidence interval testing to say,'these nodes have a y value that is substantially different, we'll count that as a discrete value'.
    #use a checkbox for this - 'use logic'.
    #this MAY BE a separate tool.. but.. if there's only two groups, allow to user to select one or the other
    #do a 'search within' tool
    #nice to add a 'set all these knobs' to xxx function
    #add a 'if these are the same, make them clones' function
    import math
    import random
    #import copy
    

    def copy_func(f):
        import types
        import functools    
        """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)"""
        g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
        g = functools.update_wrapper(g, f)
        return g

    def canSortOld(nodes, sortFunction):### REVERSED DIRECTION!!!!
        #can I sort nodes based on a given function?
        import os #just in case - better to do this as proper def function for sorts that need it.
        #print [sortFunction(node) for node in nodes]
        try:
            resultSet= set([sortFunction(node) for node in nodes])
            if len(resultSet)> 1:
                return resultSet
        except:
            return

    def canSort(nodes, sortFunction):
        #can I sort nodes based on a given function? If so, return an example
        import os, itertools # better to do this as proper def function for sorts that need 'os'.
        try:
            g= itertools.groupby(nodes, sortFunction)
            if next(g, True) and not next(g, False):
                return False
            else:
                #print sortFunction(nodes[0])
                return [sortFunction(node) for node in nodes]#this will be a tuple and never False
        except:
            return False


    def getImage(node, type):
        #sample image
        
        #scale to one pixel
        rf= nuke.nodes.Reformat()
        rf['type'].setValue('to box')
        rf['box_width'].setValue(1)
        rf['box_height'].setValue(1)
        rf['resize'].setValue('distort')
        rf.setInput(0, node)
        #sample
        rr= rf.sample('red', 0, 0)
        gg= rf.sample('green', 0, 0)
        bb= rf.sample('blue', 0, 0)
        #delete
        nuke.delete(rf)
        if type=='image luminance':
            return rr+ gg+ bb
        elif type == 'image weighted luminance':
            return rr* .3+ gg* .59+ bb* .11
        elif type == 'image redness':
            base= float(gg+ bb)
            if not base: return 0
            return rr/ base
        elif type == 'image greenness':
            base= float(rr+ bb)
            if not base: return 0
            return gg/ base
        elif type == 'image blueness':
            base= float(rr+ gg)
            if not base: return 0
            return bb/ base

    def pad_node_numbers(nodeName):
        import re
        match= re.match(r"(.+?)([0-9]+\Z)", nodeName, re.I)
        if match:
            characters, digits = match.groups()
            return "%s%09d"%(characters, int(digits))
        else:
            return nodeName



    def grid_max(inputValue, gridValue):
        #returns ceiling value
        return int(math.ceil(inputValue/ float(gridValue))* gridValue)
    

    def grid_min(inputValue, gridValue):
        #returns floor value
        return (inputValue// gridValue)* gridValue
    

    def get_sortKey(ask= True):
        #find which nodes we can sort on, 
        #if "ask", present list to user
        #build dictionary:
        #{'nice name of function to display':lambda function}
        #lambda functions are based on knobs, metadata and other specialist functions
        #would be nice to return a set of values, function to label the discrete results - e.g. uppermost directory name)
        
        #function sorts: always evaluate these:
        functionSorts= {
        'padded_name': lambda node: pad_node_numbers(node.name().lower()), #need to do a version of this that takes into account that Node10 > Node1
        'class': lambda node: node.Class(),
        'disabled': lambda node: node.disabled(),
        'errored nodes': lambda node: node.error(),
        'bounding box width': lambda node: node.bbox().w(),
        'bounding box height': lambda node: node.bbox().h(),  # add these back later
        'bounding box left': lambda node: node.bbox().x(),
        'bounding box bottom': lambda node: node.bbox().y(),
        'bounding box x center': lambda node: node.bbox().x()+ (node.bbox().w()* .5),
        'bounding box y center': lambda node: node.bbox().y()+ (node.bbox().h()* .5),
        'bounding box right': lambda node: node.bbox().x()+ node.bbox().w(),
        'bounding box top': lambda node: node.bbox().y()+ node.bbox().h(),
        'bounding box area': lambda node: node.bbox().h()* node.bbox().w(),
        'channels': lambda node:node.channels(),
        'number of channels': lambda node:len(node.channels()),
        'number of dependents': lambda node:len(node.dependent()),
        'number of dependencies': lambda node:len(node.dependencies()),
        'first frame': lambda node:node.firstFrame(),
        'last frame': lambda node:node.lastFrame(),
        'frame length': lambda node:node.lastFrame()- node.firstFrame(),
        'number of knobs': lambda node:len(list(node.knobs().items())), #this might slow everything down
        'number of metadata keys': lambda node:len(list(node.metadata().items())), # might slow everything down
        'op hashes': lambda node: node.opHashes(), # op hashes - see https://learn.foundry.com/nuke/developers/113/ndkdevguide/advanced/hashing.html
        }

        #THIS IS JUST A HACK BECAUSE I CANT GET IT TO WORK ABOVE:
        #functionSorts['file name']= lambda node:node['file'].value()#this might slow everything down
        
        
        
        #print functionSorts
        sortPossiblesFunction= {}
        for niceName, sortFunction in list(functionSorts.items()):
            #print niceName, sortFunction
            canSortResult= canSort(nodes, sortFunction)#tuple of results for each node
            if canSortResult:
                sortPossiblesFunction[niceName]= (sortFunction, canSortResult)
        #print sortPossiblesCustom.items()
        
        
        
        
        #METADATA
        #build set of metadata common to all nodes
        #metadata can flow through any node, it's not just based on image files.
        try:
            nodemetaset= set.intersection(*[set(node.metadata().keys()) for node in nodes]  )
        except AttributeError: #No metadata in one of the nodes
            nodemetaset= set()
        
        sortPossiblesMeta= {}
        if nodemetaset:
            for metaKey in nodemetaset: #was sorted
                sortFunction= lambda node: node.metadata(metaKey)
                canSortResult= canSort(nodes, sortFunction)
                #print sortKey, canSortResult
                if canSortResult:
                    #{lambda sort function: (position in list, nice name of function including values, function to label discrete results)
                    sortPossiblesMeta[metaKey]= (sortFunction, canSortResult)
    
        
        #KNOBS
        #build set of knobs common to all nodes
        totalknobset= set.intersection(*[set(node.knobs().keys()) for node in nodes]  )
        #print 'totalknobset=', totalknobset
        #build dictionary of sort functions and test:
        #if all values are not the same, add to the dictionary
        #of possible knobs and how to access them
        sortPossiblesKnobs= {}
        for knobKey in totalknobset: #was sorted

            #special case for format knobs
            #print node[knobKey].Class()
            if all(node[knobKey].Class() == 'Format_Knob' for node in nodes):
                #knobKey= knobKey #so this doesnt change later in the loop and mess up the lambda
                #sortFunction= lambda node, knobKey= knobKey: node[knobKey].value().name()# .lower() fails if None
                sortFunction= lambda node, knobKey= knobKey: (node[knobKey].value().name() or '').lower()#straight 'lower' fails if None
                canSortResult= canSort(nodes, sortFunction)
                #print 'format',canSortResult
                if canSortResult:
                    sortName= knobKey+ ' name'
                    sortPossiblesKnobs[sortName]= (sortFunction, canSortResult)

            #special case for file knobs
            elif all(node[knobKey].Class() == 'File_Knob' for node in nodes):
                #knobKey= knobKey #so this doesnt change later in the loop and mess up the lambda
                sortFunction= lambda node, knobKey= knobKey: node[knobKey].value()
                canSortResult= canSort(nodes, sortFunction)
                #print 'file', canSortResult
                if canSortResult:
                    sortName= knobKey+ ' value'
                    sortPossiblesKnobs[sortName]= (sortFunction, canSortResult)

                #evaluate lower case
                sortFunction= lambda node, knobKey= knobKey: node[knobKey].evaluate().lower()
                canSortResult= canSort(nodes, sortFunction)
                if canSortResult:
                    sortName= knobKey+ ' evaluate (lower case)'
                    sortPossiblesKnobs[sortName]= (sortFunction, canSortResult)
                #sortPossiblesCustom[niceName]= sortFunction
                #evaluate basename lower case
                #knobKey= knobKey #so this doesnt change later in the loop and mess up the lambda
                if all(node[knobKey].evaluate() for node in nodes):
                    sortFunction= lambda node, knobKey= knobKey: os.path.basename(node[knobKey].evaluate().lower())
                    canSortResult= canSort(nodes, sortFunction)
                    if canSortResult:
                        sortName= knobKey+ ' evaluate basename (lower case)'
                        sortPossiblesKnobs[sortName]= (sortFunction, canSortResult)

                    #evaluate dirname
                    sortFunction= lambda node, knobKey= knobKey: os.path.dirname(node[knobKey].evaluate().lower())
                    canSortResult= canSort(nodes, sortFunction)
                    if canSortResult:
                        sortName= knobKey+ ' evaluate dirname (lower case)'
                        sortPossiblesKnobs[sortName]= (sortFunction, canSortResult)   

                    #evaluate file extension
                    sortFunction= lambda node, knobKey= knobKey: os.path.splitext(node[knobKey].evaluate())[-1].lower()
                    if canSort(nodes, sortFunction):
                        sortName= knobKey+ ' extension'
                        sortPossiblesKnobs[sortName]= (sortFunction, canSortResult)   
            
            # MUST add specific functions per knob, e.g. array knobs, not just
            # lambda node: node[knobKey].value()
    
            else:
                sortFunction= lambda node, knobKey= knobKey: node[knobKey].value()
                canSortResult= canSort(nodes, sortFunction)
                #print knobKey, canSortResult
                if canSortResult:
                    sortPossiblesKnobs[knobKey]= (sortFunction, canSortResult)
            #print 111111111111111111111111
            #print sortPossiblesKnobs.items()
        
        
        #add these possibilities (though there's no corresponding *function* in the dictionary)
        sortPossiblesCustom= {
        'random': (None, None),
        'no sort': (lambda node: node, None),
        'image luminance': (lambda node: getImage(node, 'image luminance'), "select to analyse"),
        'image weighted luminance': (lambda node: getImage(node,'image weighted luminance'), "select to analyse"),
        'image redness': (lambda node: getImage(node, 'image redness'), "select to analyse"),
        'image greenness': (lambda node: getImage(node, 'image greenness'), "select to analyse"),
        'image blueness': (lambda node: getImage(node, 'image blueness'), "select to analyse"),
        }
        #def def_func(x): return x == 2


        #join the dictionaries
        sortKeyDir= {}
        sortKeyDir.update(sortPossiblesFunction)
        sortKeyDir.update(sortPossiblesKnobs)
        sortKeyDir.update(sortPossiblesMeta)


        if ask:
            #add the option to sort by custom (not computed yet)
            sortKeyDir.update(sortPossiblesCustom)

            #print 'sortKeyDir', sortKeyDir
            
            #make the keys into a sorted list to present to user
            sortPossiblesNice=[]
            for i in [sortPossiblesKnobs, sortPossiblesFunction, sortPossiblesCustom, sortPossiblesMeta]:
                a= sorted(i.keys())
                #print
                #print p,a
                sortPossiblesNice+= [j for j in a]
            #sortPossiblesNice= sorted(sortKeyDir.keys())# for i in [sortKeyDir]


            #put favourite items top of list:
            toplist= ['xpos', 'ypos', 'name', 'class']
            for i in reversed(toplist):
                try:
                    sortPossiblesNice.insert(0, sortPossiblesNice.pop(sortPossiblesNice.index(i)))
                except ValueError: 
                    pass            

            
            print(('sortPossiblesNice', sortPossiblesNice))
            sortPossiblesNice= ['{}'.format('\\ '.join(i.split())) for i in sortPossiblesNice]
            sortKeys= (' ').join(sortPossiblesNice)
            
            
            #add example data - convert to string and truncate
            #info = (data[:75] + '..') if len(data) > 75 else data
            
            #create the UI to ask what you want to sort by
            p= nuke.Panel('Arrange Nodes')
            
            p.addEnumerationPulldown('sort by', sortKeys)
            
            p.addBooleanCheckBox('reverse', sortReverse)
            
            #add arrangement possibilities:
            arrangeFormatNice= ['horizontal', 'vertical', 'square', 'circle', 'scatter', 'only adjust x', 'only adjust y']
            arrangeFormat= []
            for i in arrangeFormatNice:
                arrangeFormat.append('\\ '.join(i.split()))
            arrangement= (' ').join(arrangeFormat)
            p.addEnumerationPulldown('arrange', arrangement)
            
            p.addBooleanCheckBox('separate discrete values', sortDiscrete)
            
            p.addBooleanCheckBox('snap to grid', sortSnap)
            
            #show the panel
            ret= p.show()
            if ret:
                #return the lambda function
                for k,v in list(sortKeyDir.items()):
                    print((k,v)) #all the 
                #print "p value sort by", [p.value('sort by')][0]
                #print "P VALUE", sortKeyDir[p.value('sort by')][0], p.value('reverse'), p.value('arrange'), p.value('snap to grid'), p.value('separate discrete values')  
                return (sortKeyDir[p.value('sort by')][0], p.value('reverse'), p.value('arrange'), p.value('snap to grid'), p.value('separate discrete values')    )
            else:
                return (None, None, None, None, None)#
        else:
            #return all sortKeyDir
            return sortKeyDir





    ###################################################            
    ###################################################            
    ###################################################            
    ###################################################            
    #MAIN
    #need at least input nodes to sort
    if len(nodes) < 2:
        #print "name",__name__ 
        #print "file",__file__
        if "arrange_by" not in __name__:
            return        
        else:
            return nuke.critical("Please select more than one node to sort!")
        
        
        
    if sortKey == None:
        #ask the user
        sortKey, sortReverse, sortArrange, sortSnap, sortDiscrete= get_sortKey()
        if sortKey == None: 
        # maybe I should return False if we want to abort? there's nothing to sort on?
        #user aborted, or there was nothing to sort on (unlikely). Let's abort here.
            return "No sort key chosen! Specify with keyword, e.g. 'sortKey= lambda x: node['name'].value()' or choose from the gui popup."


    #else sort by chosen key
    #print result to the script editor output window
    #print '(sort by '+ sortKey+ ')'

    elif sortKey == 'random':
        random.shuffle(nodes)
        nodeSortResult= dict()
        for i, node in enumerate(nodes):
            nodeSortResult[node]= i
            sortKey= (lambda node: nodeSortResult[node], None)
    elif sortKey in ('image luminance', 'image weighted luminance', 'image redness', 'image greenness', 'image blueness'):
        imageResult= []
        for node in nodes:
            imgResult= getImage(node, sortKey)
            imageResult.append(imgResult)
            nodeSortResult= dict(list(zip(nodes, imageResult)))
            sortKey= (lambda node: nodeSortResult[node], None)
    elif sortKey == "all":
        #return all possibilities on which to sort  
        #print "here"
        return get_sortKey(ask= False)
    
    #####sort the nodes! #####
    #print sortKeyDir#[sortKey]
    #for node in nodes:
    #    print node.name(), sortKeyDir[sortKey][0], node[[sortKey][0]]
    print(('sortKey=', sortKey))
    #if sortKey!= 'no sort':
    nodes.sort(key= sortKey, reverse= sortReverse)
       
    #for node in nodes:
    #    print node.name(), sortKey(node)


    #discrete groups
    import itertools # better to do this earlier! Remember you have to sort the data before grouping -groupby method actually just iterates through a list and whenever the key changes it creates a new group. Be careful about having different sortDiscrete criteria to those which we sorted on!!!
    groupNodes= []#group of similar nodes
    if sortDiscrete:
        if sortDiscrete == 1 or sortDiscrete == True:
            #use sortKey to determine grouping. Else use whatever lambda function is in sortDiscrete.
            sortDiscrete= copy.deepcopy(sortKey)
        print(('[sortDiscrete(node) for node in nodes]',[sortDiscrete(node) for node in nodes]))
        for k, g in itertools.groupby(nodes, sortDiscrete):
            groupNodes.append(list(g))      # Store group iterator as a list
            
        print(('groups', groupNodes))
   
    else:
        groupNodes.append(nodes)

    #print groupNodes

    #prepare to arrange
    if sortSnap:
        [nuke.autoplaceSnap(node)for node in nodes]
        # Space grid width apart
        gw= nuke.toNode("preferences")["GridWidth"].value()
        #print 'gw',gw
        gh= nuke.toNode("preferences")["GridHeight"].value()
        #print 'gh',gh
        colAdd= grid_max(max([node.screenWidth() for node in nodes]), gw)
        rowAdd= grid_max(max([node.screenHeight() for node in nodes]), gh)
    else:
        colAdd= max([node.screenWidth() for node in nodes])
        rowAdd= max([node.screenHeight() for node in nodes])

    #get current node positions
    startx= min([node['xpos'].value() for node in nodes])
    starty= min([node['ypos'].value() for node in nodes])
    endx= max([node['xpos'].value() for node in nodes])
    endy= max([node['ypos'].value() for node in nodes])
        
    #horizontal
    if sortArrange == 'horizontal':
        colPos= startx
        rowPos= starty
        colCount= 0
        rowAdd*= 6
        for i, group in enumerate(groupNodes):
            for j, node in enumerate(group):
                #print node.name(), i, j 
                #start a new row each group
                node.setXYpos(int(((j* colAdd)+ startx)), int(((i* rowAdd))+ starty))

            if sortDiscrete:
                #add backdrop node def m_Backdrop(selNodes= nuke.selectedNodes(), label= None):
                original_selection= nuke.selectedNodes()

                import seanscripts.backdrop_sd
                seanscripts.backdrop_sd.make_backdrop(selNodes= group, label= sortDiscrete(group[0]))
                [i.setSelected(1) for i in original_selection]

    
    #vertical
    elif sortArrange == 'vertical':
        colPos= startx
        rowPos= starty
        colCount= 0
        for i, group in enumerate(groupNodes):
            for j, node in enumerate(group):
                #print node.name(), i, j 
                #start a new column each group
                node.setXYpos(int(((i* colAdd)+ startx)), int(((j* rowAdd))+ starty))
    
    #square
    elif sortArrange == 'square':
        colPos= startx
        rowPos= starty
        count= 0
        for i, group in enumerate(groupNodes):
            columns= int(math.ceil(math.sqrt(len(group))))#number of columns~rows
            for j, node in enumerate(group):
               node.setXYpos(int((((j% columns)* colAdd)+ startx)), int((((j// columns)* rowAdd))+ starty))
            #update node positions
            startx= max([node['xpos'].value() for node in group])+ (colAdd*3)

    
    #scatter
    elif sortArrange== 'scatter':
        hx= endx- startx
        hy= endy- starty
        for i, group in enumerate(groupNodes):
            for j, node in enumerate(group):
                node.setXYpos(int(random.random()* hx+ startx), int(random.random()* hy+ starty))
    
    #circle
    elif sortArrange == 'circle':
        #start with the smallest group and work outwards
        #sort the groups based on len(group)
        groupNodes.sort(key= lambda x: len(x))
        #centre:
        cx= startx+ (endx- startx)/ 2
        cy= starty+ (endy- starty)/ 2
        oldlen= None##if groups have the same no. of nodes, move centre to right so they don't overlap.
        for i, group in enumerate(groupNodes):
            if oldlen == len(group):
                cx+= colAdd* 3* oldlen
            #smallest radius where the nodes don't overlap:
            #r= (math.hypot((colAdd), (rowAdd))*len(group))/ 2
            r= ((colAdd+rowAdd)/ 2* len(group))/ 2
            oldlen= len(group)
            for j, node in enumerate(group):
                #update node positions
                node.setXYpos(int(math.sin(j* math.pi* 2/ float(len(group)))* r+ cx), int(math.cos(j* math.pi* 2/ float(len(group)))* r+ cy)    )
    
    #adjust x/y only: in future, have 2 pulldowns for x, y. Ability to 'set x to value' rather than sort.
    #adjust x only
    elif sortArrange == 'only adjust x':
        for node in nodes:
            node['xpos'].setValue(startx)
            startx+= colAdd
    
    #adjust y only
    elif sortArrange == 'only adjust y':
        for node in nodes:
            node['ypos'].setValue(starty)
            starty+= rowAdd
    
    return



#Qc
#by Sean Danischevsky 2018
#
#Use nuke frameranges eg 5-500x4 1-2
#Report back:
#Method range
#File size 1-40x5,41
#Channels 1000 (3)
#Max r. 1001-1234 (123222.22323)
#Min r. 1001-1200
#
import nuke


def make_read(image):
    #node= nuke.createNode('Read')
    node= nuke.nodes.Read()#faster
    node['file'].fromUserText('%s' % (image))  #safest/easiest to do this way and not too slow.
    #node.setSelected(True) #I'll do this for all later
    return node


#I Tried this:
#Use logspace (0-1) :
#a-b could be -1 to 1 so add 1 then mult by 0.5 then add .5
#Result: a lot of grey (.5) VALUES. subtle changes were too close to this to be visible. But could be useful for AI approach. Got to be careful which is A and which is B, as the results are inverted if you swap.

def nuke_nodes_to_filepaths(nodes= nuke.selectedNodes('Read')):
#input selected nuke read nodes
#return list of tuples [(FPS, first frame last frame), (...), ...]
    returnlist= []
    for node in nodes:
        returnlist.append((node['file'].value(), node['first'].value(), node['last'].value()))

    #remove duplicates
    returnlist= list(set(returnlist))   
    return returnlist




def setup_compare_seqs(nodes= nuke.selectedNodes("Read"), output= None):
    #input 2 nuke nodes
    #optional output FPS for visual comparison
    #return printed comparison of metadata/channel/image info and OPTIONAL image sequence of difference between them.
    #Compframes=[create read for f in frange()]
    #Scanframes =Same
    if nodes == None:
        try:
            nodes= nuke_nodes_to_filepaths(nodes= nuke.selectedNodes('Read'))
        except:
            return nuke.message("I need two file paths to compare.\nPlease select two read nodes.") 
    #visual compare
    delete_list= []
    with nuke.root(): #otherwise it's created inside the group, if called with nuke.thisNode()
    #with node:
        #mg= nuke.nodes.MatchGrade()
        #delete_list.append(mg)
        #mg.setInput(0, nodes[1])
        #mg.setInput(1, nodes[0])
        #oldNodes= nuke.allNodes()
        #mg['alignTargetToSource.'].execute()
        #newNodes= nuke.allNodes()- oldNodes()
        #tf= nuke.allNodes('Transform')[0]
        #rf= nuke.allNodes('Reformat')[0]
        #print tf,rf
        compare= nuke.nodes.Merge2()
        delete_list.append(compare)
        compare.setInput(0, nodes[0])
        compare.setInput(1, nodes[1])
        compare['operation'].setValue('difference')
        cv= nuke.nodes.CurveTool()
        cv['ROI'].fromScript('0 0 input.width input.height')
        delete_list.append(cv)
        cv.setInput(0, compare)
        write_node= None
        return (nodes, cv, write_node, delete_list) 






#if __name__ == '__main__':
    #compare_seqs(nuke.selectedNodes(), output= None)

def compare_seqs(nodes= nuke.selectedNodes()):
    nodes, cv, write_node, delete_list= setup_compare_seqs(nodes, output= None)
    resultDir={}
    
    
    #nuke.executeMultiple([cv,], ([sf, ef, step],))
    
    sf= min([node['first'].value() for node in nodes])
    ef= max([node['last'].value() for node in nodes])
    step= 1
    renderRange= "%d-%dx%d"% (sf, ef, step)
    #for f in range(sf, ef+ 1, step):
        #nuke.frame(f)
        #
    
    try:
        #nice taskname for progress bar
        task= nuke.ProgressTask('Checking')
        
        frame_list= nuke.FrameRanges(renderRange).toFrameList() or []
        for i, f in enumerate(frame_list):
            if task.isCancelled():
                break
            # UPDATE PROGRESS BAR
            task.setMessage( 'Frame %s' % ( f) )
            task.setProgress( int( float(i) / float(len(frame_list))* 100) )
    
            nuke.frame(f) #actually go to the frame, so as to get the right name... surely this is overkill but doesn't seem to take long at all
            #src= nuke.filename(srcNode, nuke.REPLACE)
            #dest= nuke.filename(destNode, nuke.REPLACE)
            nuke.execute(cv, f, f)
            #print
            #
            resultDir[f]= arrange_by(nodes, sortKey= "all", sortReverse= False, sortArrange= 'horizontal', sortSnap= True, sortDiscrete= False)
    except Exception as e:
        nuke.message(str(e))
        #print e
    finally:
        del(task) 
        #[nuke.delete(node) for node in delete_list]
    
    from collections import defaultdict
    flip = defaultdict(list)
    for frame, results in list(resultDir.items()):
            #print 'res',results
            framelist= []
            for k,v in list(results.items()):
                #print k,v[1]
                if k not in ['xpos', 'ypos', 'file value', 'name', 
                'nuke/node_hash', 'input/mtime', 'input/ctime', 
                'file evaluate basename (lower case)', 'input/filename', 
                'file evaluate (lower case)', 'nuke/version', 
                'number of dependents','format name', 'selected']:#if HERO SHOT == exr:#'input/filesize'
                    flip[k].append(frame)
    #collate results for printing
    
    result_text= "\n".join([node['file'].value() for node in nodes])+"\n"
    #print
    for results, frames in sorted(flip.items()):
        flip[results]= str(nuke.FrameRanges(sorted(frames)))
        #print results, flip[results]
        #print flip[results], results
        result_text+= "%s %s\n"% (flip[results], results)
    #create note with results
    note_node= nuke.nodes.StickyNote()
    # set it to the right,top of the selected Nodes
    gw= nuke.toNode("preferences")["GridWidth"].value()
    #format note on left:
    note_node['label'].setValue("<left>"+ result_text)
    note_node.setXYpos(int(max([node.xpos() for node in nodes])+ gw+ note_node.screenWidth()), int(max([node.ypos() for node in nodes])))

    return note_node
#for results, frames in flip.items():
    #print flip[results], results
#print
#for k,v in flip.items():
#    print k,v

#xpos
#ypos
#file value
#name
#nuke/node_hash
#input/mtime
#input/ctime
#file evaluate basename (lower case)
#input/filename
#file evaluate (lower case)
#nuke/version



#summarise per frame range
#dict would be
#{'seq/seq.%04d.dpx' {1001:('number of metadata keys',<function>, 23),1002:('number of metadata keys',<function>, 23)}
#{'seq/seq2.%04d.dpx' {1001:('number of metadata keys',<function>, 1),1002:('number of metadata keys',<function>, 1)}
#{'seq/seq3.%04d.dpx' (input sequence 2)...

#number of metadata keys:  
#0:23 1001-1233, 21:1234
#1:21 1001-1234

#input/ctime 
#0:2018-09-06 16:50:44 1001, 2018-09-06 16:50:44 1002, 2018-09-06 16:50:44 1003, 2018-09-06 16:50:44 1004
#1:2018-09-06 16:50:49 1001, 2018-09-06 96:50:44 1002, 2018-09-06 16:59:44 1003, 2018-09-06 16:90:44 1004



#what TO DO if a dn b are not the same length?  
    #make reads 
    #aframes= make_read("%s %s-%s"% (a[0], a[1], a[2]))
    #bframes= make_read("%s %s-%s"% (b[0], b[1], b[2]))
    #visual compare
    #compare= nuke.nodes.Merge2()
    #compare.setInput(0, a)
    #compare.setInput(1, b)
    #set to difference
    #use curvetool to find max diff on each frame.
    #If output FPS:
    #W=Write
    #Execute render
    #Run other views - save as multilayer exr?
    #Tests: If all curvettol black
    #Etc
    #Compare smart vectors between scan and comp?






    #keep these examples:
    #arrangeby( nodes= nuke.selectedNodes(),  sortKey= lambda node: node['file'].value().lower(), sortDiscrete= lambda node: node['file'].value().split(os.path.dirname(os.path.commonprefix([node['file'].value() for node in nodes])))[1].split('/')[1])  
    #arrangeby( nodes= nuke.allNodes('Read'), sortKey= lambda node: node['file'].value().lower(), sortDiscrete= lambda node: node['file'].value().split(os.path.dirname(os.path.commonprefix([node['file'].value() for node in nodes])))[1].split('/')[1])  
    #arrangeby( nuke.allNodes('Read'), sortKey=lambda node: node['file'].value().lower(), sortDiscrete= lambda node: node['file'].value()  )
    #arrangeby(nuke.selectedNodes(), sortKey= lambda node:node.channels(), sortDiscrete= True)
    #arrangeby( nuke.allNodes(), sortKey= lambda node: node.Class(), sortDiscrete= True, sortArrange='circle')
#else:
    #add it to the menu: Shift+L
    

#THE PROBLEM IS: LAMBDA DOESNT SEE ALL THE NODES, JUST ONE, SO COMMON PREFIX DOESNT WORK

#prob best to have a dir where the lambdas are the keys?
#add backgrounds with filenames
#then add timers to say how many nodes/how long it took to show the menu and layout the nodes.
#'keep in place' arrangement: reorders nodes but keeps original positions
#add image aspect, box aspect to customs


#rather than groupby to group and discover if knobs all the same, create dictionary with {result of sortDiscrete lambda: [nodes with this value]}
#e.g. if no sortDiscrete, 
#dict = {'allnodes': [node1, node2, node3, node4]}
#or if there is, then:
#dict_for_lambda_how_many_channels = 
#{
#    4: node1
#    3: node3, node4
#    1: node2
#}
#dict_for_lambda_filename =
#{
#    '
#}
# you can only search on '3' (len(nodes)>2). So add that.
#then create dictionary with {result of sortKey lambda: [nodes with this value]}
#e.g. for 'node.name()':
#{
#  'name1': node1  
#  'name2': node2  
#  'name3': node3  
#  'name4': node4  
#}
#then for each node
#then, if needed, sort by sortKey, 
#
#for hcd, lambda = based on:
#nodes=nuke.selectedNodes()

#for node in nodes:
#    print node.name(), node['file'].value().split(os.path.dirname(os.path.commonprefix([node['file'].value() for node in nodes])))[1].split('/')[1]
    #print node.name(), os.path.dirname('/'.join(node['file'].value().split(os.path.dirname(os.path.commonprefix([node['file'].value() for node in nodes])))[1].split('/')[1:]))
    #print os.path.dirname((node['file'].value().split(os.path.commonprefix([node['file'].value()) for node in nodes])[1]   .split('/')[-1]
# '''
#.split('/')[-2]#always a / in  nuke
#i.e.
#????????????????????????????//
#
# add 'pick outlier', 'bifuricate' algorhythms - computer chooses what to sort on.
# add a version which picks(sortDiscrete= 'outlier') but doesn't sort.

#os.path.commonprefix([node['file'].value() for node in nodes])

#runs when testing:
if __name__ == "__main__":
    arrange_by(nuke.selectedNodes())
    #compare_seqs(nodes= nuke.selectedNodes())
    #pass







