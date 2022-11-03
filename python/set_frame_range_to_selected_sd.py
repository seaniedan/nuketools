
import nuke

def set_frame_range_to_selected(readNodes):
	#Set Nuke script frame range from given Read Nodes
	#Sean Danischevsky 2015.
	if readNodes:
		nuke.root().knob('first_frame').setValue(min( [node['first'].value() for node in readNodes] ))
		nuke.root().knob('last_frame').setValue(max( [node['last'].value() for node in readNodes] ))
	else:
		nuke.message("No Read nodes given!")
