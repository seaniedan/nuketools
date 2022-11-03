import nuke


def copy_to_clipboard(clipboard_text):
    """
    moves text to copy buffer
    fixed for nuke 11
    :param clipboard_text: str
    :return: none
    """
    try:
        #QApplication moved to widgets 
        from PySide2.QtWidgets import QApplication
    except ImportError:
        from PySide.QtGui import QApplication

    try:
        app= QApplication.instance() # checks if QApplication already exists 
    except: 
        # create QApplication if it doesnt exist 
        app= QApplication(sys.argv)

    clipboard= app.clipboard() 
    
    clipboard.setText(str(clipboard_text))





def split_range_tens():
    # Gets the frame range and creates a string of first frame, last frame and every 10th frame in between

    fStart = int(nuke.root().knob('first_frame').value())
    fEnd = int(nuke.root().knob('last_frame').value())
    p= nuke.ask('Copy range\n{}-{}\nto clipboard, as first, last, x10s?'.format(fStart, fEnd))

    #show the panel
    if p:
        # Create stepped string
        renderOrder= [fStart, fEnd]
        renderme= set(range(fStart, fEnd+ 1))
        renderTenths= list(range(fStart, fEnd, 10))
        renderOrder+= renderTenths[1:]
        rest= list(renderme-set(renderOrder))
        renderOrder+= sorted(rest)
        frameSplit = ",".join([str(i) for i in renderOrder])

        # puts frameSplit in the clipboard

        copy_to_clipboard(frameSplit) # set clipboard
    else:
        print("Range not copied.")






def split_range_gaps():
    # Gets the frame range and creates a string of first frame, last frame and every 10th frame in between
    fStart = int(nuke.root().knob('first_frame').value())
    fEnd = int(nuke.root().knob('last_frame').value())
    p= nuke.ask('Copy range\n{}-{}\nto clipboard, as first, last, biggest gaps?'.format(fStart, fEnd))

    #show the panel
    if p:
        # Create stepped string
        renderOrder= [fStart, fEnd]
        gaps= True #go into loop
        while gaps:
            A= list(sorted(renderOrder))
            #print 'sorted renderOrder',A
            gaps= [x+ (y- x)// 2 for x, y in zip(list(A)[:-1], list(A)[1:]) if x+ (y- x)// 2 not in A]
            #print 'gaps', gaps
            renderOrder+= gaps
            #print 'final renderOrder', renderOrder

        frameSplit = ",".join([str(i) for i in renderOrder])

        # puts frameSplit in the clipboard
        copy_to_clipboard(frameSplit) # set clipboard
    else:
        print("Range not copied.")


