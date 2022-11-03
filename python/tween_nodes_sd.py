import nuke

def tween_nodes(nodes):
    #######
    #tween_nodes by Sean Daniscehevsky 2014
    #Make blend between two nodes
    #Or average many nodes together.
    #e.g. select two transform nodes with different transforms
    #     and create a number of nodes between them
    #     or a single average.
    #If you select more than one node of the same class,
    #take the left and right most nodes, delete the ones in between
    #and offer to recreate the same number of nodes, tweened.
    #TODO:
    #look at shake style clone to get list of knobs to exclude (pop x and y)
    #    and how to set array knobs etc
    #maybe find the min and max values of knobs in selected nodes
    #(not necessarily of the same class)
    #and distribute even incremented values between the existing nodes
    #it would be great to ask which knobs you want to increment between
    #esp. when we get to search in text nodes etc for numbers
    #e.g. write sdlfkj_v001....dkljskj_v002.....
    #
    #This would really be a different tool, but
    #a hyper-cool way to do this would be to
    #use an aninmation curve in one node
    #and for each 'frame' create a node with the values at that frame.  
    #print len(nodes)
    #
    #
    #it'd be great to be able to do an average of 4 axis nodes to get the centre.
    #or the average of a selection of constants.
    #
    #I'd like to search for numbers in strings and interpolate them - but maybe that's too complex.
    #It should really error if there's an approximation/error going on.
    #Width/Height knobs (type 'WH_Knob') e.g. in transform scales don't tween if the length of one is longer than the other
    #e.g. if you have one scale set to 1 and another to [1,2]. 

    #print (nodes)
    if len(nodes) == 1:
        return nuke.message(f"Selected node: {nodes[0].name()}.\nI need at least two nodes to tween between! Perhaps you're in a group?")

    if len(nodes) < 2:
        return nuke.message("I need at least two nodes to tween between!\nPlease select at least two nodes of the same class.")
      
    #all nodes same class?
    if len(set([node.Class() for node in nodes])) > 1:
       return nuke.message("I can only blend between nodes of the same class!\nPlease select at least two nodes of the same class.")

    #ask how many tween nodes to make
    if len(nodes) == 2:
        bkDefault= 3
        bkDisplay= bkDefault
        question= 'Total number of nodes in the range\n(e.g. %i nodes creates %i tween node):'%(bkDisplay, bkDisplay-2)
    else:
        #prepare to delete the middle selected nodes, and set node 0 and 1 to be left and rightmost!
        #x is reversed in node graph so I choose min for max and vice versa
        minmax= [min(nodes, key= lambda x: x['xpos'].value()), max(nodes, key= lambda x: x['xpos'].value())]
        bkDefault= len(nodes)
        bkDisplay= bkDefault
        question= 'Delete selected nodes between\n%s\nand\n%s\nand create tweens to make a total of:'%(minmax[0].name(),minmax[1].name())
    panel= nuke.Panel("Tween between Nodes by Sean Danischevsky")
    panel.setWidth(300)
    panel.addSingleLineInput(question, bkDisplay)
    if panel.show(): #display panel. Input from user.
        if panel.value(question) == "" or panel.value(question) == bkDisplay: 
            #user writes nothing. myRange= total nodes including orignals
            myRange= int(bkDefault)
        else:
            myRange= int(panel.value(question))
    else:
            raise Exception('User cancelled')
            return "User cancelled"

    #delete extra nodes (left and right Nodes are minmax)  
    if len(nodes) > 2:      
        [nuke.delete(node) for node in nodes if node not in minmax]
        nodes= minmax

    #to do - 
    #would be nice to be able to set anywhere where there is a number, even in expressions, e.g. [time+0]...[time+100]
    #what to do with curves? in the future I'd like to create nodes to tween between the animation curves.
    #list of knobs types we would like to interpolate
    #interpolateList=[]

    excludedKnobs= ["name"]#, "xpos", "ypos"]

    #deselect the nodes so the new nodes don't get connected. (Can't use nuke.nodes.XXX() to make abitrary class :-(  ).
    [node['selected'].setValue(False) for node in nodes]
    
    #create the nodes
    for i in range(myRange):
        #ignore first and last
        if i!= 0 and i!= myRange- 1:
            #don't create first and last nodes, they already exist
            #print "Creating node %i of %i"%(i+ 1, myRange) 
            node= nuke.createNode(nodes[0].Class(), inpanel= False )
            x= i/ float(myRange- 1)
            #print 'mix:', x
            knobs= node.knobs()
            for knob in knobs:
                if knob not in excludedKnobs:
                    #print knob
                    try:
                        upper, lower= [nodes[0][knob].value(), nodes[1][knob].value()]#min and max
                        node[knob].setValue([(j* x)+ k*(1- x) for j, k in zip(upper, lower)])
                        #print knob,'Sucess!'
                    except TypeError: 
                        #e.g. TypeError: zip argument #1 must support iteration
                        try:
                            node[knob].setValue((x* upper)+ (1- x)* lower)
                            #node[knob].setValue(float( lower+ i*(upper- lower))/ float(n) )
                            #node[knob].setValue( int(float((lower+ i*(upper- lower)/ (n-1) ))))
                            #print knob,'Sucess!'
                        except:
                            #copy values from first selected node
                            node[knob].fromScript(nodes[0][knob].toScript(False))
                            pass
                    except:

                        pass

          

            #set common inputs
            if nodes[0].inputs() and [nodes[0].input(j) for j in range(nodes[0].inputs())] == [nodes[1].input(j) for j in range(nodes[0].inputs())]:
                #minmax nodes have same input, set inputs for the others
                [node.setInput(j, nodes[0].input(j)) for j in range(nodes[0].inputs())]
            
            #set common outputs
            commonOutputs= set(nodes[0].dependent(nuke.INPUTS)).intersection(set(nodes[1].dependent(nuke.INPUTS)))
            if commonOutputs:
                #minmax nodes have same outputs, set outputs for the others
                #TODO: this is a lot more complicated than I first thought. What if you have independent inputs  as well as your tween inputs, or outputs go into input 2,3,4? Anyway, this seems to work.
                #print (commonOutputs)
                [commonOutput.connectInput(0, node) for commonOutput in commonOutputs] 
                
            #finally, prepare to select it
            nodes.append(node)
    #reselect the nodes
    [ node['selected'].setValue(True) for node in nodes ]

    return


###########################
#runs when testing:
if __name__ == "__main__":
    tween_nodes(nuke.selectedNodes())



