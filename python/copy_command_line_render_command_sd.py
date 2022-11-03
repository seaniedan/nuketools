import nuke

def copy_command_line_render_command_to_clipboard():

    #copy command line render command to clipboard
    #
    #by Sean Danischevsky 2020
    #

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
            import sys
            app= QApplication(sys.argv)

        clipboard= app.clipboard() 
        
        clipboard.setText(str(clipboard_text))


    def render_command():
        #returns command_line render command
        nodes= nuke.selectedNodes('Write')
        sgNodes= nuke.selectedNodes('WriteTank')
        nodes+= sgNodes
        #if sgNodes:

        nodeNames= ",".join(node.name() for node in nodes)
        execuable= nuke.env['ExecutablePath']
        scriptName= nuke.scriptName()#nuke.root()['name'].value() #correctly returns '' if script isn't saved
        renderRange= '{}-{}'.format(nuke.root().firstFrame(), nuke.root().lastFrame())
        command_to_copy= '{} -X {} {} {}'.format(execuable, nodeNames, scriptName, renderRange)
        return command_to_copy


    copy_to_clipboard(render_command())
