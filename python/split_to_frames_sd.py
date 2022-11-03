import nuke

def split_to_frames(nodes):  
    #split to frames
    #by sean danischevsky 2015
    #take selected Read node sequence and create a Read node per frame
    #only reads for now - any need to split geo etc?

    import os
    if nodes:
        for node in nodes:
            for f in range(node['origfirst'].value(), node['origlast'].value()+ 1):
                #create read for each frame, copying values from original node
                n= nuke.createNode(node.Class(), 
                    node.writeKnobs(nuke.WRITE_USER_KNOB_DEFS | nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_SCRIPT), 
                    inpanel= False)
                #set frame
                n['first'].setValue(f)
                n['last'].setValue(f)
                n['origfirst'].setValue(f)
                n['origlast'].setValue(f)
            #delete original node
            nuke.delete(node)

    else: 
        nuke.message("Select some Read nodes to create a Read node per frame.") 
        return

def split_to_frameholds(nodes):  
    #split to frames
    #by sean danischevsky 2015
    #take selected Read node sequence and create a Framehold node per frame
    #only reads for now - any need to split geo etc?

    import os
    if nodes:
        for node in nodes:
            for f in range(node['origfirst'].value(), node['origlast'].value()+ 1):
                #create FrameHold for each frame
                fh= nuke.createNode('FrameHold')
                fh['first_frame'].setValue(f)
                fh.setInput(0, node)
                fh['postage_stamp'].setValue(1)
    
    else: 
        nuke.message("Select some Read nodes to create a FrameHold per frame.") 
        return


###########################
#runs when testing:
if __name__ == "__main__":
    split_to_frames(nuke.selectedNodes("Read"))
