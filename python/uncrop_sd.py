import nuke

def uncrop(nodes= nuke.selectedNodes('Crop')):
    #input selected Crop nodes with reformat on
    #output crop node which puts the cropped area back in the original position

    #hold any warnings
    warn= []

    #hold new nodes
    newnodes= []

    #main loop
    for node in nodes:
        #get the details
        x, y, r, t= node['box'].value()
        try:
            width= node.input(0).width() 
            height= node.input(0).height()
        except: 
            width= nuke.root().width()
            height= nuke.root().height()
            warn.append(node)

        #make new node
        newnode= nuke.nodes.Crop()

        #set position, input and parameters
        newnode.setXYpos(node.xpos(),node.ypos()+node.screenHeight())
        newnode.setInput(0, node)
        newnode['box'].setValue((-x, -y, width-x, height-y))
        newnode['reformat'].setValue(True)
        newnode['crop'].setValue(True)

        #name the new node
        newNameFormat= "%s_uncrop" % node.name()
        if nuke.exists(newNameFormat):
            i= 1
            newNameFormat= "%s_uncrop%d" % (node.name(), i)
            while nuke.exists(newNameFormat): 
                i+= 1
                newNameFormat= "%s_uncrop%d" % (node.name(), i)
        newnode.setName(newNameFormat)
        newnodes.append(newnode)

    #report warnings
    if warn:
        msg= "Some nodes didn't have inputs, please check:\n%s"% (', '.join((i.name() for i in warn)))
        nuke.message(msg)
    return newnodes
