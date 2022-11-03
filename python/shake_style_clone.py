#  nShakeClone.py
#  Nuke Python Module
#
#  Recreates a shake style "uni-directional" clone
#
#  Created by Jesse Spielman on 8/26/2010
#  jesse@themolecule.net
#
#       version 1.0 on 8/26/2010
#       Initial release
#
#       version 1.1 on 10/25/2010
#       bugfix suggested by Hugh Macdonald to work around cloning array_knobs using setSingleValue()
#
#       version 1.2 on 3/10/2011
#       improvement suggested by Michael Habenicht to handle String Knobs
#
#       version 1.3 on 3/10/2012
#       Added comments / removed some debug statements
#
#       v1.3c
#       hide panel
#       added Hugh's code for renaming
#
#  Take all selected nodes and create dupliates that are linked via expressions
#  to the node for all knobs except those an EXCLUSION_LIST...there may be
#  value in defining different EXCLUSION_LISTs per node class...
#
#  Copyright 2010 The Molecule.
#  http://www.themolecule.net
#  All rights reserved.
#
#  Software is provided "as is," which means no guarantees!
 
import nuke
 
def shakeClone(nodes):
        EXCLUSION_LIST = ['autolabel', 'cached', 'disable', 'dope_sheet', 'filter', 'fringe', 'gl_color', 'help', 'hide_input', 'indicators', 'inject', 'knobChanged', 'label', 'Mask', 'maskChannelInput', 'maskChannelInput', 'maskChannelMask', 'maskChannelMask', 'maskFrom', 'maskFromFlag', 'name', 'note_font', 'note_font_color', 'note_font_size', 'onCreate', 'onDestroy', 'panel', 'postage_stamp', 'postage_stamp_frame', 'process_mask', 'selected', 'tile_color', 'transform', 'updateUI', 'xpos', 'ypos']
# other knobs that caused problems before the mods:
# "fbx_load_take_node_names", "file_menu", "file", "fstop", "matrix", "snap_menu", "useMatrix", "world_matrix"'
 
        #deselect all nodes
        #[ node['selected'].setValue(False) for node in nuke.allNodes() ]
        #print nodes
        for node in nodes:
                new= nuke.createNode(node.Class(), inpanel= False )
               
                for i in node.knobs():
                    if i not in EXCLUSION_LIST:
                        #if node.knob(i).visible():#that didn't work - xpos still 'visible'
                        # Try to set the expression on the knob
                        new.knob(i).setExpression("%s.%s" % (node.name(), node.knob(i).name()))
                        # This will fail if the knob is an Array Knob...use setSingleValue to compensate
                        # Thanks Hugh!
                        if isinstance(new.knob(i), nuke.Array_Knob):
                                new.knob(i).setSingleValue(node.knob(i).singleValue())
                        # This will fail if the knob is a String Knob...use a TCL expression link to compensate
                        # Thanks Michael!
                        elif isinstance(new.knob(i), nuke.String_Knob):
                                new.knob(i).setValue("[value %s.%s]" % (node.name(), node.knob(i).name()))
                                       
                new['selected'].setValue(True)
                new.setInput(0, None)                #set name
                newNameFormat = "%s_clone%%d" % node.name()
                i= 1
                while nuke.exists(newNameFormat % i): i+= 1
                new.setName(newNameFormat % i)
        #return nodes to selected state
        #[ node['selected'].setValue(True) for node in nodes ]


##################################
#runs when testing:
if __name__ == "__main__":
    shakeClone(nuke.selectedNodes())

