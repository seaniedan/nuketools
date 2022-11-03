#####MAKE THUMBNAILS by Sean Danischevsky 2011
#need to add some code so it removes nodes upstream and doesn't remake jpegs for those.
#add menu to specify a location to save jpegs
#add dilate on alpha so text is more legible
#check for the whole list if file exists and create one warning for all files. (currently ignores check and overwrites?)
# doesnt work on shots where file not saved and no filename at top of chain.


import nuke, os


def open_dir_in_browser(dir):
    import os, sys, subprocess

    if sys.platform == 'darwin': 
        os.system('open %s'% dir) 

    elif sys.platform == 'linux2': 
        try:
            #os.system('caja %s' % dir)
            subprocess.Popen('/usr/bin/caja  \"%s\"' % dir, shell= True)
        except:
            try:
                os.system('xdg-open \"%s\"'% dir) #why os.system not popen?

            except:
                try:
                    os.system('export LD_LIBRARY_PATH=/usr/lib64:$LD_LIBRARY_PATH ; nautilus \"%s\"' % dir)
                except:
                    nuke.message("Can't find a file browser!\nTry adding one in open_dir_in_browser (copy_file_to_clipboard_sd.py)")

    elif sys.platform == 'win32': 
        dir= dir.replace('/', os.sep) 
        os.system('explorer \"%s\"' % dir)
    
    return



def _copyKnobsFromScriptToScript(n, m):
  k1 = n.knobs()
  k2 = m.knobs()
  excludedKnobs = ["name", "xpos", "ypos"]
  intersection = dict([(item, k1[item]) for item in list(k1.keys()) if item not in excludedKnobs and item in k2])
  for k in list(intersection.keys()):
    x1 = n[k]
    x2 = m[k]
    x2.fromScript(x1.toScript(False))
        

def findUpstreamNodes(st_node_set, nd_input): 
    #puts all the nodes into a set, and does not recurse if a node is already in the set 
    for i_input_idx in range( nd_input.inputs() ): 
        if nd_input.input(i_input_idx) not in st_node_set: 
            st_node_set.add(  nd_input.input(i_input_idx)  ) 
            findUpstreamNodes(st_node_set, nd_input.input(i_input_idx)) 

def filterNodeSet(st_node_set, lst_node_class_list): 
    #filter out nodes of a Class or Classes 
    st_filtered_set= set() 
    for node in st_node_set: 
        if node.Class() in lst_node_class_list: 
            st_filtered_set.add(node) 
    return list(st_filtered_set) 



def make_tn(sn, rn, _panel):
    #make a thumbnail image in Nuke
    #returns the path of the image created 
    import sys, os, shutil
    file= rn['file'].evaluate()
    name= os.path.basename(file)
    root= name.split('.')
    name= root[0]  #will cause problems if there are unexpected numnber of dots in filepath
    #print _panel.value('Save path'), _panel.value("Image format")
    jpgPath= _panel.value('Save path').replace( "\\", "/" )+ "/"+ name+ "."+ str(_panel.value("Image format"))

    # Create nodes
    delnodes= []  #nodes to delete after render
    vpNode= nuke.ViewerProcess.node()
    '''try:
        lut = lut.makeGroup()
    except:
        #lut = lut.writeKnobs(nuke.WRITE_USER_KNOB_DEFS | nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_SCRIPT)
        import copy
        lut = copy.copy(lut)

    try:
        lut['label'].setValue(lut['current'].value()) #this was causing problems
    except:
        pass'''

    [i['selected'].setValue(False) for i in nuke.allNodes()]
    lut = nuke.createNode(vpNode.Class())
    _copyKnobsFromScriptToScript(vpNode, lut)


    lut.setInput(0, sn)
    delnodes.append(lut)

    cs= nuke.nodes.Colorspace()
    cs['colorspace_in'].setValue('srgb')
    cs.setInput(0, lut)
    delnodes.append(cs)

    rf= nuke.nodes.Reformat()
    rf.setInput(0, cs)
    rf['type'].setValue("to box")
    rf['box_width'].setValue(int(_panel.value('Width')))
    delnodes.append(rf)

    if not os.path.exists(nuke.defaultFontPathname()) and nuke.NUKE_VERSION_MAJOR> 8:
        #use new text node
        tt= nuke.nodes.Text2()
        tt['font_size'].setValue(150)
    else: #font path exists
        tt= nuke.nodes.Text()
        tt['font'].setValue(nuke.defaultFontPathname())
        tt['size'].setValue(150)

    tt['message'].setValue(name)
    tt['box'].setValue([0, 0, 12112, 777])
    tt['xjustify'].setValue("center")
    tt['yjustify'].setValue("bottom")
    tt['cliptype'].setValue("no clip")
    delnodes.append(tt)

    dil= nuke.nodes.Dilate()
    dil.setInput(0,tt)
    dil['channels'].setValue('alpha')
    dil['size'].setValue(20)
    delnodes.append(dil)

    ct= nuke.nodes.Crop()
    ct.setInput(0, dil)
    ct['box'].setExpression('input.bbox.x', 0)
    ct['box'].setExpression('input.bbox.y', 1)
    ct['box'].setExpression('input.bbox.x+ input.bbox.width',2)
    ct['box'].setExpression('input.bbox.y+ input.bbox.height',3)
    ct['reformat'].setValue("True")
    delnodes.append(ct)

    rft= nuke.nodes.Reformat()
    rft.setInput(0,ct)
    rft['type'].setValue("to box")
    rft['box_width'].setValue(int(_panel.value('Width')))
    delnodes.append(rft)

    blk= nuke.nodes.BlackOutside()
    blk.setInput(0,rft)
    delnodes.append(blk)

    mg= nuke.nodes.Merge2()
    mg.setInput(0, rf)
    mg.setInput(1, blk)
    mg['selected'].setValue(True)
    delnodes.append(mg)

    wo= nuke.nodes.Write()
    wo.setInput(0,mg)
    wo['file'].setValue(jpgPath)
    wo['file_type'].setValue(_panel.value("Image format"))
    if _panel.value("Image format") == "jpg":
        wo['_jpeg_quality'].setValue(.95)
    delnodes.append(wo)

    # Optionally add text
    mg['disable'].setValue(1-_panel.value("Burn-in filename"))

    # Optionally embed LUT
    if not _panel.value("Embed current LUT"):
        lut['disable'].setValue(1)
        cs['disable'].setValue(1)

    #render or not
    if _panel.value("Keep reformat nodes and do not render"):
        # warn if the JPEG exists
        if os.path.exists(jpgPath):
            #delete and remake?
            msg= "Note: the thumbnail\n%s\nexists!" % (jpgPath)
            nuke.message(msg)
        return
    else:
        #render the jpegs
        #does the JPEG already exist?
        asked= False
        if os.path.exists(jpgPath):
            #delete and remake?
            msg = "The thumbnail\n%s\nexists. Delete and re-create?" % (jpgPath)
            asked = True
            delete_existing_file= nuke.ask(msg)
            if (delete_existing_file):
                try:
                    os.unlink(jpgPath)
                except:
                    msg = "Could not delete\n%s" % (jpgPath)
                    nuke.message(msg)
                    return
            else:
                #exit if user cancels
                return

        nuke.execute(wo, nuke.frame(), nuke.frame())

        #load the TN 
        rm= nuke.createNode("Read")
        rm['file'].fromUserText(jpgPath)
        rm['xpos'].setValue(rn.xpos())
        rmyval= rn.ypos()- 111
        rm['ypos'].setValue(rmyval)

        #delete the nodes 
        for delnode in delnodes:
            nuke.delete(delnode)
        return jpgPath

def make_thumbnail(nodes, _panel):
    #make thumbnail for each node
    #returns a list of files made
    ret= []
    for node in nodes:
        if node.Class() == "Read":
            ret.append(make_tn(node, node, _panel))
        else:
            st_upstream_node_list= set() 
            findUpstreamNodes(st_upstream_node_list, node) 
            st_read_node_list= filterNodeSet(st_upstream_node_list, ["Read"])
            if st_read_node_list:
                topnode= st_read_node_list[0]
                ret.append(make_tn(node, topnode, _panel))
                #else, assume the upstream node has no read node, so we can't get a filename!
    return ret

def make_thumbnails(nodes):
    #if no read node selected, exit
    if not nodes:
        nuke.message('No nodes selected! Select nodes from which to make thumbnails.')
    else:
        panel= nuke.Panel("Make thumbnails")
        #panel.addSingleLineInput('width', 200)
        panel.addExpressionInput("Width", "width/1")
        panel.addClipnameSearch('Save path', os.path.join(os.path.expanduser("~"), 'thumbnails'))
        panel.addBooleanCheckBox("Burn-in filename", True)
        panel.addBooleanCheckBox("Embed current LUT", True)
        panel.addBooleanCheckBox("Keep reformat nodes and do not render", False)
        panel.addEnumerationPulldown("Image format", "jpg png")
        panel.setWidth(400)
        if panel.show():
            images= make_thumbnail(nodes, panel)

            try:
                #print 'images', images
                #open_dir_in_browser(panel.value('Save path'))
                open_dir_in_browser(os.path.dirname(images[0]))
            except:
                pass

    return


##################################
#runs when testing:
if __name__ == "__main__":
    make_thumbnails()

