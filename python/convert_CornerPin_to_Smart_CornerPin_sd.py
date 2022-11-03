import nuke

def convert_CornerPin_to_Smart_CornerPin(nodes):
    ####convert cornerpin to smartcornerpin####
    #by Sean Danischevsky 2016
    #assumes data is in CornerPin2d
    #in first tab
    #adds reference frame
    #input = nuke nodes you want to affect.
    nodes= [node for node in nodes if node.Class() == 'CornerPin2D']

    if nodes:
        for node in nodes:
            #add integer knob for reference frame
            node.addKnob(nuke.Int_Knob('ref_frame', 'reference frame')) 
            #set to current frame
            node['ref_frame'].setValue(nuke.frame())
            #add 'set to this frame' button
            node.addKnob(nuke.PyScript_Knob('set_ref_frame','set to current frame'))
            node['set_ref_frame'].setCommand('nuke.thisNode()[\'ref_frame\'].setValue(nuke.frame())')
            #rename 'User' tab that gets created
            node['User'].setLabel('Tracking')         

            #add the code to the 'from' tab
            node['from1'].clearAnimated()
            node['from1'].setExpression('to1(ref_frame)')
            node['from2'].clearAnimated()
            node['from2'].setExpression('to2(ref_frame)')
            node['from3'].clearAnimated()
            node['from3'].setExpression('to3(ref_frame)')
            node['from4'].clearAnimated()
            node['from4'].setExpression('to4(ref_frame)')

            #add label to show reference frame
            node['label'].setValue('Reference: [value ref_frame]')

    return nodes


def convert_mochaTracker(nodes):
    ####convert Tracker4 to use T,R,S and set reference frame####
    #by Sean Danischevsky 2018
    
    #input = nuke nodes you want to affect.

    #turn on TRS 
    #stabilise 
    #set reference frame to current 
    #Turn of TrackerKeyframes 

    nodes= [node for node in nodes if node.Class() == 'Tracker4']

    if nodes:
        for node in nodes:
            k= node['tracks'] 
            numColumns= 31 
            #node['tracks'].toScript() 
            #node['tracks'].fromScript()
            Tracker4Columns= ["enable", "name", 
            "track_x", "track_y", 
            "offset_x", "offset_y", 
            "T", "R", "S", 
            "error",  "error_min", "error_max", 
            "pattern_x", "pattern_y", "pattern_r", "pattern_t", 
            "search_x", "search_y", "search_r", "search_t"]

            #Set T,R,S on 
            #trackIdx_track_x = k.getValue(numColumns*trackIdx + Tracker4Columns.index("track_x")) 
            for trackIdx in range(4):
                for col in ["T", "R", "S"]:
                    a= numColumns* trackIdx+ Tracker4Columns.index(col)
                    k.setValue(1.0, a)

            #stabilise 
            #node['transform'].setValue('stabilize')

            #match-move 
            node['transform'].setValue('match-move')            

            #set reference frame to current 
            node['reference_frame'].setValue(nuke.frame())

            #Turn off TrackerKeyframes because they delay rendering in the UI
            node['keyframe_display'].setValue(3)

            #Turn on livelink because otherwise the ransformation doesn't appear unless you're looking at it
            node['livelink_transform'].setValue(True)

    return nodes

###########################
def fix_mocha_tracker_or_cornerpin(nodes):
    changed_nodes= convert_CornerPin_to_Smart_CornerPin(nodes)+ convert_mochaTracker(nodes)

    if changed_nodes:
        return changed_nodes
    else:
        nuke.message("Please select some CornerPin2D or Tracker nodes!")     

