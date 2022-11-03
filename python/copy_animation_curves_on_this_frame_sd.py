import nuke
#for now, this just copies 'translate', 'rotate', 'scale' between two selected nodes.
#hmmm... think I need to save knob names and curves rather than
#animation curve python objects, as they will change
#when script is reloaded.

#to do:

#select two nodes
#work out shared knobs 
#bring up GUI to confirm source, dest knobs/curves
#check knobs have animation
#if source doesbn't have animation, can't use it
#if dest doesn't have animation, make it

#maybe make a 'copy' button on the dest node,
#and list the curves that will be copied.

#copy translate, rotate and scale for current frame
#set up from and to, and what to copy with GUI 
#copying from tracker to transform node

#TODO: set undo status, so you can undo curve sets.

def setup(nodes):
    #source_node= nuke.toNode('Tracker_Layer_3')
    #dest_node= nuke.toNode('Transform1')
    source_node=nodes[0]
    dest_node=nodes[1]
    print((source_node.name()))
    print((dest_node.name()))
    
    #build dict of source:dest animation curves
    curve_dict= {}
    knobs= ['translate', 'rotate', 'scale']
    source_curves= [source_node[knob].animations() for knob in knobs]
    for knob in knobs:
        for source_curve, dest_curve in zip(source_node[knob].animations(), dest_node[knob].animations()):
            curve_dict[source_curve]= dest_curve
    return curve_dict

curve_dict= setup(nuke.selectedNodes())

def copy_values_to_keyframe(curve_dict, frame):
    #make animation curve yourself first
    #and set transform to invert yourself for now
    #inputs:
    #curve_dict: dict of source:dest nuke animation curves
    #frame = integer (or float if you really want) keyframe
    for source_curve, dest_curve in list(curve_dict.items()):
        #print frame
        #print source_curve.evaluate(frame)
        #copy from source to dest:
        dest_curve.setKey(frame,source_curve.evaluate(frame))

copy_values_to_keyframe(curve_dict, nuke.frame())

