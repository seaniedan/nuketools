#################################
#list missing frames
#by Sean Danischevsky 2015
#select a read or write node and copy a list of missing frames
#TODO: would like it to work by finding first and last
#rendered frames, not relying on node's start, end.
#would like to work on multiple reads/writes and proxy
#ignore files like /mnt/projects/oc/work/seand/000/060/nuke/render/precomp/rainBottomB/v006/oc_sc000_sh060_rainBottomB_v006.1088.png.2977.tmp
#and .nk files
#can I use glob/
import nuke
import os

#testing= True
testing= False


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


def clipboard_text():
    """
    returns text from copy buffer
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
    
    return clipboard.text()

def list_missing_frames(nodes):
    #given a list of (single) Nuke node, 
    #report missing frames
    #and ask if you want to copy the list to clipboard
    missingFiles= []
    completeFileName= ""
    
    # first check if a node is selected and if so if it is a read node
    #selectedNodes = nuke.selectedNodes()
    
    # either nothing or too much is selected
    if (len(nodes) != 1):
        nuke.message("Please select a single node!")
        return 
        
    #now we are sure one read node is selected, so go on.
    node= nodes[0]
    
    #use 'file knob' to get path, 
    try:
        fileNameLong= node['file'].getValue()
        #print fileNameLong
        if node.Class() == 'Write' and not node['use_limit'].value():
            startFrame= int(nuke.root()['first_frame'].value())
            #print startFrame
            endFrame= int(nuke.root()['last_frame'].value())
            #print startFrame        
        else:
            startFrame= int(node['first'].getValue())
        #print startFrame
            endFrame= int(node['last'].getValue())
        #print startFrame

    except:
        return nuke.message("Please select a node with a file knob, e.g. a read node!")
    
    # split the long file name with path to its subsections    
    pathName, fileNameShort = os.path.split(fileNameLong)

    splitFileName = fileNameShort.split(".")
    
    '''if (len(splitFileName) != 3):
        nuke.message("File does not have the format name.number.ext.\nSearch the missing frames yourself :)")
        return'''
        
    fileName= splitFileName[0]
    filePaddingOrg= splitFileName[-2]
    filePaddingLength= len((filePaddingOrg) % 0)
    fileExtension= splitFileName[-1]
   
    
    # search for missing files in the sequence 
    for i in range(startFrame, endFrame+ 1):
        # first build the string of the padded frameNumbers
        frameNumber= str(i)        
        
        while(len(frameNumber)< filePaddingLength):
            frameNumber= "0"+ frameNumber
        fileNameAndExt= fileName+ "."+ frameNumber+ "."+ fileExtension
        completeFileName= os.path.join(pathName, fileNameAndExt)
        #print completeFileName
        if not os.path.isfile(completeFileName):
            missingFiles.append(i)
    
    if(len(missingFiles) == 0):
        nuke.message("No missing files in range %d-%d!"%(startFrame, endFrame))
        return
            
    cleanedUpMissingFiles = str(nuke.FrameRanges(missingFiles))
    print(cleanedUpMissingFiles)
    p= nuke.ask("In the range: "+ str(startFrame)+ "-"+ str(endFrame)+ "\nthe following files are missing:\n\n"+ cleanedUpMissingFiles+ '\nCopy to clipboard?')
    #p= nuke.ask('Copy range\n{}-{}\nto clipboard, as first, last, x10s?'.format(fStart, fEnd))
    #p.addEnumerationPulldown('Sort by', sortKeys)
    #sortReverse=False
    #p.addBooleanCheckBox('reverse',sortReverse)
    #add arrangement possibilities:
    #arrangeFormatNice=['horizontally','vertically','in a square','in a circle','scatter']
    #arrangeFormat=[]
    #for i in arrangeFormatNice:
    #arrangeFormat.append('\\ '.join(i.split()))
    #arrangement= (' ').join(arrangeFormat)
    #p.addEnumerationPulldown('Arrange', arrangement)
    #separateDiscrete=False
    # p.addBooleanCheckBox('separate discrete values',separateDiscrete)
    #snapToGrid=True
    #p.addBooleanCheckBox('snap to grid',snapToGrid)
    #show the panel
    if p:
        copy_to_clipboard(cleanedUpMissingFiles) # set clipboard 
        print(("Range copied: {}".format(clipboard_text())))
    else:
        print("Range not copied.")


#runs when testing:
if __name__ == "__main__":
    list_missing_frames()
