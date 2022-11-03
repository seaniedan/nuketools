import nuke

###########################
### copy instead of render
### by sean danischevsky 2017





def move_and_symlink(src, dst):
        #sean 2017
        import os
        #should really check if we're on win32 and can do symlinks
        #os_symlink = getattr(os, "symlink", None)
        #if callable(os_symlink) ....do the below, else just copy as usual.
        if os.path.islink(src):
            #can't set permissions for symlinks on Linux. Copy the files instead.
            shutil.copy(os.path.realpath(src), dst)
            return 'Source was already a symlink: copied the original file.'
        else:
            os.rename(src, dst)
            os.symlink(dst, src)
            return 'Moved and symlinked.'

def move_file(src, dst):
    #sean 2017
    #move file src to dst
    #will move symlinks rather than the original file
    import os
    os.rename(src, dst)
    return 'Moved.'

def copy_file(src, dst):
    #sean 2017    
    #copy src to dst. If src is a symlink, copy2 copies the target file.
    import os
    import shutil
    shutil.copy2(src, dst)
    return 'Copied.'

def link_file(src, dst):
    #sean 2017
    #hard link src and dst. If src is a symlink, link the target file.
    import os
    if os.path.islink(src):
        #don't want to hardlink symlinks. Link to the original file instead.
        os.link(os.path.realpath(src), dst)
    else:
        os.link(src, dst)
    return 'linked.'


def copy_file(src, dst):
    #sean 2017    
    #copy src file to dst file
    #if src is a symlink, shutil will copy the target of the symlink to dst
    #copy doesn't preserve permissions etc, which is good
    import os
    import shutil
    shutil.copy(src, dst)
    return 'Copied.'


def upstream(startNode, nodes= None, what= nuke.EXPRESSIONS|nuke.INPUTS|nuke.HIDDEN_INPUTS, enter_groups= False ):
    #by Sean Danischevsky 2018
    #return upstream Nuke nodes, recursively. Enter groups if required.
    #startNode can be a node or list of nodes.
    #You can use the following constants or'ed together to select the types of dependencies that are looked for:
    #nuke.EXPRESSIONS = expressions
    #nuke.INPUTS = visible input pipes
    #nuke.HIDDEN_INPUTS = hidden input pipes.
    #The default is to look for all types of connections.

    #these lines are required for recursive evaluation
    if nodes == None: 
        nodes= []

    #start loop
    if startNode:
        for node in nuke.dependencies(startNode, what):
            if node not in nodes:
                print('(added)')
                #add to list
                nodes.append(node)
                if enter_groups and node.Class() == "Group":
                    group= nuke.toNode(node.name())
                    with group:
                        outputs= nuke.allNodes('Output')
                        for output in outputs:
                            upstream(output, nodes= nodes, what= what)
                upstream(node, nodes= nodes, what= what)
        return list(nodes)
    else:
        return


'''
def get_dependent_nodes(nodes):
        """
        #leave this for posterity/ideas
        Takes a node or list of nodes and returns a list of all of node's dependencies.
        Uses `nuke.dependencies()`. This will work with cyclical dependencies.
        """
        try:
            all_deps= set([nodes])
        except TypeError:
            #nodes was already a list
            all_deps= set(nodes)
        all_deps.update(nuke.dependencies(list(all_deps)))
      
        seen= set()

        while True:
            diff= all_deps- seen
            to_add= nuke.dependencies(list(diff))
            all_deps.update(to_add)
            seen.update(diff)
            if len(diff) == 0:
                break

        all_deps= all_deps- set(nodes)

        return list(all_deps)
'''
    #print get_dependent_nodes(nuke.selectedNodes())

#define copy/move/link styles
#styles= {move_and_symlink:"move file, create symlink in old location", move_file:"move file", copy_file:"copy file", link_file:"hard link (file exists in both locations)"}

styles= {"move file, create symlink in old location":(move_and_symlink,'moving and symlinking'), "move file":(move_file,'moving'), "copy file":(copy_file,'copying'), "hard link (file exists in both locations)":(link_file,'linking')}

def copy_instead_of_render(destNodes, style= None, renderRange= None):
    ### inputs: destNodes= list of nuke nodes to write to, e.g. Write, WriteGeo nodes.
    ### style= Can be 'copy', 'link', 'symlink', 'move', 'move and create symlink in old location'. If None, it will ask for a style in the GUI.
    ### renderRange= Nuke format range of frames to copy, e.g. '1001-1500'. If None, it will prompt in the GUI. If False, it will render the whole input range without asking.
    ### output = copies source file to destination instead of rendering through nuke
    ###
    ### to do - allow rendering more than one node.
    ### - add functionality for other types of node, e.g. vectors
    ### which might mean looking for the same class of node instead of 'Reads'
    ### try setting up dummy read and write nodes to copy these files using this version
    import shutil
    import os




    #check the classes
    destNodes= [node for node in destNodes if node.Class() in ['Write', 'WriteTank']] # need my recursive read dictionary here, SO i CAN COPY SMARTVECTORS ETC
    if len(destNodes)> 1:
        return nuke.message("Just one write node at a time!\nMessage sean-at-danischevsky.com if you need more.")
    elif len(destNodes)< 1:
        return nuke.message("Couldn't find a write node!\nPlease select one.")
    #for each write node, find a single read Node
    else:
        #let's return here after rendering
        original_frame= nuke.frame() 
        for destNode in destNodes:
            srcNodes= upstream(destNode)
            print(('srcNodes=', ",".join([srcNode.name() for srcNode in srcNodes])))
            srcNodes= [node for node in srcNodes if node.Class() == 'Read']
            if len(srcNodes) == 1:
                #only one input file, we can go ahead
                srcNode= srcNodes[0]
                sf= srcNode.firstFrame()
                ef= srcNode.lastFrame()
                if (renderRange == None) or (style == None):
                    #bring up dialogue with first and last frames selected
                    #in future, display one line for each sequence
                    panel= nuke.Panel("Copy/Move/Link instead of render")
                    #panel.setWidth(220)
                    #style=move_file
                    #add possibilities:
                    arrangeFormatNice= sorted([i for i in list(styles.keys())])

                    arrangeFormat= []
                    for i in arrangeFormatNice:
                        #if there's a space, use a slash to ignore it (else it would become another option)
                        arrangeFormat.append('\\ '.join(i.split()))
                    #join the options with spaces
                    arrangement= (' ').join(arrangeFormat)
                    p_style= 'Copy/Move/Link style'
                    panel.addEnumerationPulldown(p_style, arrangement)
                    display= '%d-%d'%(sf, ef) #display range to render
                    p_range= 'Range:'
                    panel.addSingleLineInput(p_range, display)
                    p= panel.show()
                    if p: #display panel. Input from user.
                        #list of individual frames to render
                        renderRange= panel.value(p_range)
                        style= panel.value(p_style)
                        #make_and_copy(srcRead, destWrite, renderRange)
                        #return
                else:
                    #called without asking user
                    if not renderRange:
                        #but we didn't specify a range, so use the input range
                        renderRange= '%d-%d'%(sf, ef)
                #make the dirs if they don't exist... would prefer to run all the 'before render' callbacks, as there may be other callbacks we normally run. 
                #But how to access those? Not just the ones in destWrite['before render'], aren't there also invisible callbacksa? For now:
                #print destWrite.name()

                #was going to hash this -
                #import seanscripts.make_write_directories_sd
                #seanscripts.make_write_directories_sd.write_mkdir(node= destNode)#, askUser= True)
                #replaced because it didn't work with TK_Write
                #but still get error 'file knob doesn't exist'

                #should have everything we need
                destdir= os.path.dirname(nuke.filename(destNode, nuke.REPLACE))
                if not os.path.exists(destdir):
                    os.makedirs(destdir)
                if os.path.isdir(destdir):
                    try:
                        #nice taskname for progress bar
                        task= nuke.ProgressTask('%s'%style)
                        
                        frame_list= nuke.FrameRanges(renderRange).toFrameList() or []
                        for i, f in enumerate(frame_list):
                            if task.isCancelled():
                                break
                            # UPDATE PROGRESS BAR
                            task.setMessage( '%s frame %s' % (styles[style][1], f) )
                            task.setProgress( int( float(i) / float(len(frame_list))* 100) )
                
                            nuke.frame(f) #actually go to the frame, so as to get the right name... surely this is overkill but doesn't seem to take long at all
                            src= nuke.filename(srcNode, nuke.REPLACE)
                            dest= nuke.filename(destNode, nuke.REPLACE)
                            #print style
                            #print src
                            #print dest
                            #print
                            #use the chosen move/copy/symlink function
                            styles[style][0](src, dest)
                    except Exception as e:
                        nuke.message(str(e))
                    finally:
                        del(task) 
        #return to original frame
        nuke.frame(original_frame) 
    return
 






    

def make_and_copy(srcRead, destWrite, renderRange, style):
    #makes a directory and copies files
    #inputs: srcRead= a nuke node, 
    #outputdestWrite
    # renderRange= Nuke format range of frames to copy, e.g. '1001-1500'
    #make the dir
    return


###########################
#run when testing:
if __name__ == "__main__":
    copy_instead_of_render(nuke.selectedNodes())

