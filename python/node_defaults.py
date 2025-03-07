import nuke

# please keep Node Classes in alphabetical order

#cards are usually 1 row and column
nuke.knobDefault('Card2.rows', '1')
nuke.knobDefault('Card2.columns', '1')


#identity matrix for color matrix
nuke.knobDefault('ColorMatrix.matrix', '{1 0 0} {0 1 0} {0 0 1}')


#ContactSheet should be top to bottom
#really need to check how many nodes and selected and 
#make a good size number of rows/cols to fit.
#change width and height to input size if all the same or project size if not
nuke.knobDefault('ContactSheet.roworder', 'TopBottom')
nuke.knobDefault('ContactSheet.rows', '2')
nuke.knobDefault('ContactSheet.columns', '2')




#Constant - usually want white. If you want black, use a reformat:
nuke.knobDefault('Constant.color', '1')

#dissolve should always start halfway!
nuke.knobDefault('Dissolve.which', '0.5')

#EdgeDetectWrapper -usually used for mattes
nuke.knobDefault('EdgeDetectWrapper.channels', 'alpha')

#Exposure Tool: use stops instead of densities  
nuke.knobDefault('EXPTool.mode', '0')

#don't clip blacks in Grade
nuke.knobDefault('Grade.black_clamp', 'False')

#don't clip blacks in Grain
nuke.knobDefault('Grain2.minimum', '-.006')

#autokey for Roto shapes is handled in Preferences (Nodes).
#I turn it off there. But for the Gridwarp:
nuke.knobDefault('GridWarp3.toolbar_autokey', '0')
nuke.knobDefault('GridWarp3.background', 'on black')

#mirror Horizontal
nuke.knobDefault('Mirror.Horizontal', '1') 
nuke.knobDefault('Mirror2.flop', 'True') 

#pfb
nuke.knobDefault('PFBarrel.mode', 'Undistort')
nuke.knobDefault('PFBarrel.label', '[value mode]')

#Position to points should always have something, usually rgb:
nuke.knobDefault('PositionToPoints2.P_channel', 'rgb')

#don't clip paint
nuke.knobDefault('RotoPaint.cliptype', 'no clip')

#don't clip Roto
nuke.knobDefault('Roto.cliptype', 'no clip')


#let's always save smart vectors to the same place:
nuke.knobDefault('SmartVector.file', '[file dirname [knob [topnode].file]]/vectors/[lindex [split [lindex [split [knob [topnode].file] .] 0] /] end].%04d.exr')
#and full detail
nuke.knobDefault('SmartVector.vectorDetailReg', '1')
#and file path
nuke.knobDefault('SmartVector.label', '[value file]')

###STMap
nuke.knobDefault('STMap.uv', 'rgb') 
nuke.knobDefault('STMap.channels', 'all') 

#Temporal Median - I usually want 1:
nuke.knobDefault('TemporalMedian.core', '1')

#set tracker to default to 'Affine'
nuke.knobDefault('Tracker.warp', 'a')

#Turn off Tracker Keyframes which slow EVERYTHING down
nuke.knobDefault('Tracker.keyframe_display', '3')

# Write: auto crop (add ROI)with EXR files
nuke.knobDefault('Write.exr.autocrop', '1')  
nuke.knobDefault('Write.exr.interleave', 'channels and layers')  

