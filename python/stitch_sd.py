import nuke

# stitch_sd and compare selected

def stitch_sd(nodes= nuke.selectedNodes()):
    
    ##########################
    ##############
    #stitch_sd
    #by Sean Danischevsky 2017
    #
    #
    #connects pairs of nodes.
    #top to bottom
    #would be nice to select 2 classes of node defined by their proximity.
    #or work out what you want to do dependng on how 

    #To do
    #Make one to join 2 top nodes to bottom. - Chunk by 3's.
    #want it to stitch where i have read on left and right and merge in middle. - search for significant gaps in x or y
    #also look at factors - 2,3 etc.
    #doesn't work well with small mnumbers of nodes - connects wrongly

    #if replacing read nodes, ask if you want to delete old and move new ones into their position

    #but for now... 
    #Stitch 2, ask which input if there's already a connected input.


    def chunk(l, chunksize):
        return [l[i:i + chunksize] for i in range(0, len(l), chunksize)]

    #work out if we want to go top to bottom or left to right
    x_distance= max([node.xpos() for node in nodes])- min([node.xpos() for node in nodes])
    y_distance= max([node.ypos() for node in nodes])- min([node.ypos() for node in nodes])
    #if x distance between nodes is greater than y distance, connect nodes top to bottom
    if x_distance> y_distance:

        #sort by xpos
        nodes.sort(key= lambda node: node.xpos())

        #chunk into pairs
        pairs= chunk(nodes, 2)
        #sort into top, bottom
        [pair.sort(key= lambda node: node.ypos()) for pair in pairs]

        #look at inputs
        #for now just connect
        for top, bottom in pairs:
            bottom.setInput(0, top)
    else:
        #connect nodes left to right 
        #sort by ypos
        nodes.sort(key= lambda node: node.ypos())

        #chunk into pairs
        pairs= chunk(nodes, 2)
        #sort into top, bottom
        [pair.sort(key= lambda node: node.xpos()) for pair in pairs]

        #look at inputs
        #for now just connect
        for top, bottom in pairs:
            bottom.setInput(0, top)        




def stitch_check_sd(nodes= nuke.selectedNodes()):
    
    ##########################
    ##############
    #stitch_check_sd
    #by Sean Danischevsky 2017
    #
    #
    #connects pairs of nodes.
    #with CheckAligns.
    #always go left to right

    def chunk(l, chunksize):
        return [l[i:i + chunksize] for i in range(0, len(l), chunksize)]


    #connect nodes left to right 
    #sort by ypos
    nodes.sort(key= lambda node: node.ypos())

    #chunk into pairs
    pairs= chunk(nodes, 2)
    #sort into top, bottom
    [pair.sort(key= lambda node: node.xpos()) for pair in pairs]

    #look at inputs
    #for now just connect
    for top, bottom in pairs:
        ca= nuke.nodes.Compare_sd()
        ca.setInput(0, top)
        ca.setInput(1, bottom)
        ca.setXYpos(int((top.xpos()+ bottom.xpos())/ 2.0), int((top.ypos()+ top.screenHeight()/ 2.0+ bottom.ypos()+ bottom.screenHeight()/ 2.0)/ 2.0- ca.screenHeight()/ 2.0))        #print 'top',top.xpos(),top.ypos()
        #print 'top', top.xpos(),top.ypos()
        #print 'bottom', bottom.xpos(),bottom.ypos()
        #print 'ca', ca.xpos(), ca.ypos()

