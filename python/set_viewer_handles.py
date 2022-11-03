import nuke

def set_viewer_range(head_handles= 10, tail_handles= 10, ask= False):
    # set in and out points of viewer to script range minus handle frames
    # by Sean Danischevsky 2017
    
    if ask:
        p= nuke.Panel('Set Viewer Handles')
        p.addSingleLineInput('Head', head_handles)
        p.addSingleLineInput('Tail', tail_handles)
        #show the panel
        ret = p.show()
        if ret:
            head_handles= p.value('Head')
            tail_handles= p.value('Tail')
        else:
            return

    #only positive integers, please
    head_handles= max(0, int(head_handles))
    tail_handles= max(0, int(tail_handles))

    # Get the node that is the current viewer
    v = nuke.activeViewer().node()

    # Get the first and last frames from the project settings
    firstFrame = nuke.Root()['first_frame'].value()
    lastFrame = nuke.Root()['last_frame'].value()

    # get a string for the new range and set this on the viewer
    newRange = str(int(firstFrame)+ head_handles) + '-' + str(int(lastFrame) - tail_handles)
    v['frame_range_lock'].setValue(True)
    v['frame_range'].setValue(newRange)











