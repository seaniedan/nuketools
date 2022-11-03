import nuke


def set_write_range(nodes):



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


    if nodes:
        #print what we're going to do
        nodenames= ", ".join(sorted([node.name() for node in nodes]))
        print(("Setting first and last frames for %s" % (nodenames)))
    
        for node in nodes:
            node['use_limit'].setValue(True)
            node['first'].setValue(node.firstFrame())
            node['last'].setValue(node.lastFrame())
            print(("%s set to %d-%d" %(node.name(), node.firstFrame(), node.lastFrame())))
    
        #get frame range 
        firstFrame= min([node.firstFrame() for node in nodes]) 
        lastFrame= max([node.lastFrame() for node in nodes])
    
        render_range= "%d-%d"% (firstFrame, lastFrame)
        print(("Render range:%s"% (render_range)))
        #render
        #nuke.executeMultiple( nodes, (firstFrame, lastFrame, 1))
    
    
    
        p= nuke.ask('Copy range\n%s\nto clipboard\n(from %s)?'%(render_range, nodenames))
        if p:
            copy_to_clipboard(render_range)
            print(("Range copied: {}".format(render_range)))
        else:
            print("Range not copied.")
            
    else:
        nuke.message("No Write nodes found!\nSelect Write nodes to set their render ranges to input range.")

       
if __name__ == '__main__':
    set_write_range(nodes= nuke.selectedNodes('Write')+ nuke.selectedNodes('WriteTank'))


