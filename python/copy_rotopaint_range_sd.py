import nuke


def get_rotopaint_range(nodes):

    def find_paint_frames(root_layer):
        """
        :param root_layer: top layer of rotopaint curves knob that holds all shapes
        :return: set - paint strokes frames
        """
        paint_frames_list = set()  # holds a list of frames which have paint strokes for this rotopaint node
        for item in root_layer:
            if isinstance(item, nuke.rotopaint.Layer):  # if item is a layer jump inside
                find_paint_frames(node)
            elif isinstance(item, nuke.rotopaint.Stroke) or isinstance(item, nuke.rotopaint.Shape):  # if item is a stroke or shape
                stroke = item.getAttributes()
                lifetime_type = stroke.getCurve('ltt')
                if lifetime_type.evaluate(0) == 0.0:  # stroke lifetime set to all project frames
                    paint_frames_list.update(list(range(proj_first, proj_last)))
                    break 
                else: 
                    paint_frames_list |= set(paint_life_attr(stroke))  # union of two sets
        return paint_frames_list


    def paint_life_attr(stroke):
        """
        :param stroke: individual paint stroke in list
        :return: list - frames paint stroke is active on
        """
        lifetime_type = stroke.getCurve('ltt')
        lifetime_start = stroke.getCurve('ltn')
        lifetime_end = stroke.getCurve('ltm')
        if lifetime_type.evaluate(0) == 1.0:  # start to frames
            return list(range(proj_first, int(lifetime_start.evaluate(0))+1))
        elif lifetime_type.evaluate(0) == 2.0:  # single frame
            return [int(lifetime_start.evaluate(0))]
        elif lifetime_type.evaluate(0) == 3.0:  # frame to end
            return list(range(int(lifetime_start.evaluate(0)), proj_last+1))
        elif lifetime_type.evaluate(0) == 4.0:  # frame range
            return list(range(int(lifetime_start.evaluate(0)), (int(lifetime_end.evaluate(0)+1))))


    def format_frames(list_to_format):
        """
        formats the list of frames eg. 1001-1005, 1007, 1009-1011
        :param list_to_format: set
        """
        list_to_format = [x for x in list_to_format if proj_first <= x <= proj_last]
        return nuke.FrameRanges(list(sorted(list_to_format)))


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

    nodes = [node for node in nodes if node.Class() in ['RotoPaint', 'Roto']]
    #get the project frame range - we'll only work inside this
    proj_first = int(nuke.Root()['first_frame'].getValue())
    proj_last = int(nuke.Root()['last_frame'].getValue())
    paint_frames_list_all = set()  # holds a list of frames which have paint strokes for ALL selected rotopaint nodes
    
    if not nodes:
        nodes = nuke.allNodes('RotoPaint')+ nuke.allNodes('Roto')
    if not nodes:
        return nuke.message("No Roto or RotoPaint nodes found!")

    for rp_node in nodes:
        root_layer = rp_node['curves'].rootLayer  # top layer of rotopaint curves knob that holds all shapes
        paint_frames_list_all |= find_paint_frames(root_layer)
    if len(paint_frames_list_all):
        paint_frames= format_frames(paint_frames_list_all)
        nodenames= ", ".join(sorted([node.name() for node in nodes]))
        p= nuke.ask('Copy range\n%s\nto clipboard\n(from %s)?'%(paint_frames, nodenames))
        if p:
            copy_to_clipboard(paint_frames)
            print(("Range copied: {}".format(paint_frames)))
        else:
            print("Range not copied.")
        
    else:
        nuke.message("No shapes or paint strokes found\nin any Roto or RotoPaint nodes!")

       
if __name__ == '__main__':
    get_rotopaint_range(nodes= nuke.selectedNodes('RotoPaint')+ nuke.selectedNodes('Roto'))
