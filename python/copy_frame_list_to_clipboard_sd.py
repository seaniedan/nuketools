import nuke
#nuke.menu( 'Animation' ).addMenu( 'seanscripts' ).addCommand( 'Copy keyframes to frame list', "import seanscripts.copy_framelist_to_clipoard;seanscripts.copy_framelist_to_clipoard.copy_framelist()" )

def copy_framelist():
    #convert keys (which pass a certain test) to a framelist and copy to clipboard 
    #this version only returns integer keyframes
    #you could analyse all frames without keyframes given a frame range (from user)

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



    def getKnobIndex():

        #useful function by Ivan Busquets 

        tclGetAnimIndex = """

        set thisanimation [animations]
        if {[llength $thisanimation] > 1} {
            return "-1"
        } else {
            return [lsearch [in [join [lrange [split [in $thisanimation {animations}] .] 0 end-1] .] {animations}] $thisanimation]
        }
        """

        return int(nuke.tcl(tclGetAnimIndex))

    def getKnobName(knob_name_with_suffix):
        
        # THIS NEEDS IMPROVING
        # if we try to run this script on transforms applied to Beziers or Layers within a RotoPaint node, they fall under the knob "curves"
        # i.e. "curves.Bezier1.rotate" or "curves.translate.x". Nuke gets a bit weird when trying to expression link to these attributes, the 
        # naming conventions start getting randomly inconsistent. It probably all falls under the _curvelib.AnimCTransform object type. 

        knob_name = knob_name_with_suffix.split(".")[0]
        print(("knob_name " + knob_name))
        return knob_name

    #get the node and knob
    n= nuke.thisNode()
    k= nuke.thisKnob()
    print((n.name(), k.name()))
    print(("animations:", k.animations()))


    knob_names = nuke.animations() # Returns the animations names under this knob
    print(knob_names)
    #i= getKnobIndex() #find out if user only clicked on a single knob index, or the entire knob
    
    ''''print "knob index: " + str(i)

    j= 0 #index for knob
     
    for knob_name_with_suffix in knob_names: 
    
        if(i > -1):
            j = i
        
        print "for knob_name_with_suffix in knob_names:"
        
        knob_name = getKnobName(knob_name_with_suffix)
        
        # so that we can get at the knob object and do...
        k = nuke.thisNode()[knob_name]'''




    frames= []
    for curve in k.animations():

        print((curve, curve.selected()))
        #keys must be on integer frame numbers
        keys= [key.x for key in list(curve.keys()) if key.x == int(key.x)] 
        frames.extend(keys)
    #convert keys to frames
    print(frames)
    frames= list(set([int(frame) for frame in frames]))
    
    #return list of keys for which value is true 
    #x.filter xxx(xxx)

    #convert list of numbers to framelist and
    #copy framelist to clipboard
    if len(frames):
        paint_frames= nuke.FrameRanges(list(sorted(frames)))
        p= nuke.ask('Copy range\n%s\nto clipboard?'%(paint_frames))
        if p:
            copy_to_clipboard(paint_frames)
            print(("Range copied: {}".format(paint_frames)))
        else:
            print("Range not copied.")
        
    else:
        nuke.message("No keys found!")
    return 


#test on a grade node:
#n,k= nuke.selectedNode(),nuke.selectedNode()['blackpoint']
#n,k= nuke.selectedNode(),nuke.selectedNode()['whitepoint']

#https://learn.foundry.com/nuke/developers/11.3/pythondevguide/animation.html

