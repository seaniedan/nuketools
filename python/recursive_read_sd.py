
#dir with this seq hangs beacuse of fromUserText:
#/mnt/projects/elements/apw/elements/Images/telegraphPoles/notHoms/291726.jpg
#/mnt/projects/elements/apw/elements/Images/telegraphPoles/notHoms/62046198.jpg

'''
currentDir='/mnt/projects/elements/apw/elements/Images/telegraphPoles/notHoms'
a=nuke.getFileNameList(os.path.abspath(currentDir))

image=os.path.join(currentDir,a[0])
node= nuke.nodes.Read(file=fromUserText('%s'% (image)))
node= nuke.nodes.Read()#faster
node['file'].fromUserText('%s' % (image))

use something like
import re
m=re.match(r'(.+) (\d+)-(\d+)',image)
if m:
    node['file'].setValue(m.group(1))
    sf=int(m.group(2))
    ef=int(m.group(3))
    node['first'].setValue(sf)
    node['origfirst'].setValue(sf)
    node['last'].setValue(ef)
    node['origlast'].setValue(ef)

----BUT THIS HANGS TOO! as soon as last is set.
'''

###################################################
#
#
#Recursive Load 
# by Sean Danischevsky 2011, 2012, 2017
# recursively search a directory for Nuke loadable files
# and present them usefully!
# overview:
# - get dir, setup filters, prefs (or be passed these)
# - get list of dirs, check for files - done
# - check what extension
# - check with prefs what to do: 
# -           images: create seq, load seq, conv to stereo 
# -           geo: load geo
# -           camera: load camera
# -           else load into sticky note
#
#
# http://effbot.org/librarybook/os-path.htm
#Loads Nuke files - descends into directories
#To do: make it faster. Only find directories first. 
#Then ask how many levels we want to descend
#Or use 'find -type d' for speed.
#then run the single level loader on each dir.

##############################################################
# to do: revised 'paste' function:
# - assume clipboard contains *something!*
# - try regular paste - anything?
# - multiple lines?
#then for each line:
# - try removing any spaces before each line
# - try expanding any regex
# - multiple diredctories to follow? ASK - add 'always follow' option
# - Parse everything then ASK before loading:
#   show counts/files and checkboxes for different file types
# - 
# - 
# - could try ising returnDirs=True, returnHidden=True  instead of my own list dir function?
# getFileNameList(dir, splitSequences= False, extraInformation= False, returnDirs=True, returnHidden=False)
# @param dir the directory to get sequences from @param splitSequences whether to split sequences or not @param extraInformation whether or not there should be extra sequence information on the sequence name @param returnDirs whether to return a list of directories as well as sequences @param returnHidden whether to return hidden files and directories. Retrieves the filename list .
# Returns: str - Array of files.
# - 
# - 
#########################################

import nuke
import backdrop_sd

def recursive_read(walkPaths= None, maxdepth= -1, 
    extRead= ['.ari', '.avi', '.cin', '.dpx', '.dtex', '.exr', '.iff', '.gif', '.hdr', '.hdri', '.jpg', '.jpeg', '.mov', '.mp4' ,'.mxf', '.qt', '.pic', '.png', '.png16', '.psd', '.r3d', '.sgi', '.sgi16', '.rgb', '.rgba', '.tif', '.tiff', '.tif16', '.tiff16', '.ftif', '.ftiff', '.tga', '.targa', '.rla', '.yuv'], 
    extCamera= ['.cam'], extReadGeo= ['.abc', '.fbx', '.obj'], 
    extStickyNote= ['.csv', '.xml', '.txt', '.xpm'], 
    extOCIOFileTransform= ['.csp','.cms','.cube','.3dl','.blut','.vf','.cub'], 
    extOCIOCDLTransform= ['.cc','.ccc'], 
    extIgnore= ['.autosave', '.dae', '.db', '.ma', '.mb', '.mel', '.meta', '.nk', '.nk~', '.nkple', '.gizmo', '.pkl', '.pickle', '.pfcp', '.pfmp', '.psb', '.rv', '.svn-base', '.svn/all-wcprops', '.svn/entries', '.swatches', '.tmp', '.tx', '.vars', '.xmp', '.zip'], 
    includeString= None, excludeString= None, latest= False):
    # was     extVectorfield= ['.csp','.cms','.cube','.3dl','.blut','.vf','.cub'], 

    #walkPaths= a directory or list of directories (e.g. '/a/dir/' or ['/path/to/dir','/other/path'])
    #blacklist, whitelist: 
    #SHOULD do it like this:###################################################
    #nodedir= {'dpx': make_read, 
    #          'db': make_stickynote}  
    #for 'latest': only keep latest files.. in each dir/level?

    #can specify dict to use to replace this one, e.g. if you're only interested in dpx, {'dpx': 'Read'}
    import os
    import arrange_by_sd
    print(('walkPaths=', walkPaths))

    def process_dir(currentDir, files= [], depth= 0):
        #Process files within given directory currentDir
        # Get a Nuke readable list of files and dirs in currentDir
        #add to list 'fileList'
        #to call first time, use
        # process_dir(walkPath, files= [], depth= 0)

        #global depth
        filesInCurDir= nuke.getFileNameList(os.path.abspath(currentDir))
        if filesInCurDir:
            # Traverse through all files
            for file in filesInCurDir:
                curFile= os.path.join(currentDir, file)
 
                # Check if it's a normal file or directory
                if os.path.isdir(curFile) or os.path.islink(curFile):
                    # Enter into directory or link for further processing
                    if depth < maxdepth or maxdepth == -1: #if maxdepth ==-1, we descend as far as possible
                        print(("going into", curFile))
                        depth+= 1
                        process_dir(curFile, files= files, depth= depth)
                else:
                    #Add to the file list
                    files.append(curFile)
            return files
        else:
            return []

    #define the types:
    def make_read(image):
        #node= nuke.createNode('Read')
        node= nuke.nodes.Read()#faster
        node['file'].fromUserText('%s' % (image))  #safest/easiest to do this way and not too slow.
        #node.setSelected(True) #I'll do this for all later
        return node

    def make_stickynote(msg):
        filename= open(msg, "r")
        myLabel= filename.read(100)
        filename.close()
        finalLabel= ("%s\n%s") % (msg,myLabel)
        #node= nuke.createNode('StickyNote')
        node= nuke.nodes.StickyNote(label=finalLabel)
        #node['label'].setValue(finalLabel)
        return node

    def make_camera(msg):
        #node= nuke.createNode('Camera2')
        node= nuke.nodes.Camera2(file= msg, read_from_file= True)
        #read_from_file
        #node['file'].setValue(msg)
        #node['label'].setValue(msg)
        return node

    def make_readgeo(file):
        #node= nuke.createNode('ReadGeo2')
        node= nuke.nodes.ReadGeo2()
        #set prefs so we don't raise dialogues
        abcDefault= nuke.toNode("preferences")["DfltAbcAlwaysCreateAllInOne"].value()
        try:
            nuke.toNode("preferences")["DfltAbcAlwaysCreateAllInOne"].setValue(True)
            #read_from_file
            node['file'].setValue(file)
            #node['label'].setValue(file)
            node.setInput(0, None)
        except:
            msg= "Couldn't load:\n%s"%(file)
            node['label'].setValue(msg)
        finally:
            nuke.toNode("preferences")["DfltAbcAlwaysCreateAllInOne"].setValue(abcDefault)
        return node

    def make_stickynote_filename_only(msg):
        #print filename only
        finalLabel= ("%s") % (msg)
        #node= nuke.createNode('StickyNote')
        #node['label'].setValue(finalLabel)
        node= nuke.nodes.StickyNote(label= finalLabel)
        return node

    def make_vectorfield(file):
        #superceded by make_OCIOFileTransform
        node= nuke.nodes.Vectorfield(vfield_file= file)
        return node

    def make_OCIOFileTransform(file):
        #OCIO 3d LUT
        node= nuke.nodes.OCIOFileTransform(file=filepath)
        return node        

    def make_OCIOCDLTransform(file):
        #Open Color In Out Color Decision List
        node= nuke.nodes.OCIOCDLTransform(file= file, read_from_file= True)
        return node
    '''
    #need more types for classes which use files, e.g. vectorfield: ***** = priority****

    OFXuk.co.thefoundry.noisetools.denoise_v100 ['analysisfile']
    GenerateLUT ['file']
    MatchGrade ['outfile']
    SmartVector ['file']
    Text ['font'] - --- '.ttf'?
    ScannedGrain ['fullGrain']
    Viewer ['file']
    Write ['file', 'proxy']
    Read ['file', 'proxy']
    AudioRead ['file']    ******************
    DeepWrite ['file', 'proxy']
    DeepRead ['file', 'proxy']
    WriteGeo ['file']
    ReadGeo ['file']
    ParticleCache ['file'] 
    Precomp ['file']
    BlinkScript ['kernelSourceFile'] *****************
    Viewer ['file']
    Vectorfield ['vfield_file'] **************although oddly this one didn't turn up using the code below!??****
    I got this list by:


    node_list=[]
    node_dic = {}

    def getItem(menu):

        #Recursive function to browse all menus and submenus
        #of the Nodes menu to retrieve all items and commands
        #to execute them.
    
        if isinstance(menu, nuke.Menu):
            for item in menu.items():
                getItem(item)
        else:
        #the menu is actually a command
            if (menu.name() not in node_list and
                menu.name() not in node_dic.values()):
                node_dic[menu] = menu.name()


    getItem(nuke.menu("Nodes"))


    for name in node_dic.values():
        print name 


    for i in node_dic.values():
        try:
            nuke.createNode(i)
        except:
            pass


    for node in nuke.selectedNodes():
        filek=[k for k in node.knobs() if (node[k].Class()== 'File_Knob' and k != 'icon')]
        if filek:
            print node.Class(), filek  

    '''



    def nuke_loader(file):
        #load the right Class of object for given file
        #get the extension, so we know what file to load
        stripped= nuke.stripFrameRange(file)
        filenameLower= stripped.lower()
        _, extension= os.path.splitext(filenameLower)
        print((file, extension))
        if (includeString == None) or (includeString.lower() in filenameLower):
            if (excludeString == None) or (excludeString.lower() not in filenameLower):
                try:
                    _, extension= os.path.splitext(filenameLower)
                    #extension= os.path.splitext(filenameLower)[1][1:]
                    print((file, extension))
                    if extension not in extIgnore:
                        if extension in extRead:
                            return make_read(file)
                        elif extension in extStickyNote:
                            return make_stickynote(file)
                        elif extension in extCamera:
                            return make_camera(file)
                        elif extension in extReadGeo:
                            return make_readgeo(file)
                        elif extension in extOCIOFileTransform:
                            make_OCIOFileTransform(file)
                        elif extension in extVectorfield:
                            make_vectorfield(file)
                        elif extension in extOCIOCDLTransform:
                            make_OCIOCDLTransform(file)
                        else:
                            return make_stickynote_filename_only(file)
                        #pass#exlist.append(file)
                except:
                    return make_stickynote_filename_only(file)



    #HERE'S THE MAIN PROG! :-)
    if not walkPaths:
        # we've called this from the GUI: let's ask the user
        walkPaths= []#we will build a list of walkpaths

        #if nodes selected, let's see if there's a path to use in the file broswer.
        #Present the highest common path to the user.
        nodes= nuke.selectedNodes()
        if nodes:
            allowed_knobs= ["File_Knob", "String_knob", "Multiline_Eval_String_Knob"]
            try:
                for node in nodes:
                    knobs= node.knobs()
                    for knob in list(knobs.keys()):
                        if node[knob].Class() in allowed_knobs:
                            evall= node[knob].evaluate()
                            try:
                                #take the directory name of any files we find
                                vall= os.path.dirname(evall)
                                if os.path.isdir(vall):
                                    #add walkpath to list
                                    walkPaths.append(vall)
                            except:
                                pass #that knob didn't contain a file path: ignore
                if len(walkPaths)> 1:
                    walkPaths= os.path.dirname(os.path.commonprefix(walkPaths))+ os.sep
                else:
                    walkPaths= walkPaths[0]+ os.sep

            except:
                pass # no nodes selected?

        #to do  -  perhaps now we should look in the clipboard?

        potential_walkPaths= []#list of places to look for a file path
        
        if walkPaths:
            #path selected using selected nodes: show highest directory in the browser
            potential_walkPaths= (nuke.getClipname('Choose folders from which to load all files', multiple= True, default= walkPaths))

        else:
            #still no valid paths found: bring up the default file browser.
            potential_walkPaths= (nuke.getClipname('Choose folders from which to load all files', multiple= True))
        
        if potential_walkPaths:
        #try to split paths for file sequences
            for walkPath in potential_walkPaths:
               try:
                   if os.path.isdir(walkPath):
                       walkPaths.append(walkPath)
                   else:
                       #look at the containing directory
                       walkPath= os.path.split(walkPath)[0]
                       if os.path.isdir(walkPath):
                           walkPaths.append(walkPath)
               except:
                   print(("Couldn't split path", walkPath))
                   #return None
        else:
            return None
    #so now we have either a list of directories, a single directory (string) or nothing.
    if walkPaths:
        if type(walkPaths) == str:
            #turn it into a list so we always do the loop
            walkPaths= [walkPaths]

        #NEED TO GET RID OF THIS FOR LOOP: WANT IT TO MAKE A SET OF ALL THE THINGS TO LOAD, THEN MAKE MENU, THEN LOAD.
        #this  is kond of working, but better to have two processes with taskbar: 
        #1 find dirs
        #2 find seqs in thos dirs
        #
        #we've been given a walkpath of many 
        #set task bar - this is a bit silly because we only usually see one dir being read, and it hangs for a long time on big dirs.
        task= nuke.ProgressTask('Walking directories')
        for i, walkPath in enumerate(set(walkPaths)):
            if task.isCancelled():
                break
            # UPDATE PROGRESS BAR
            task.setMessage( 'Processing directory %s' % walkPath )
            task.setProgress( int( float(i) / float(len(walkPath))*100) )
            #print 'walkPath=', walkPath
            #exlist= []
            #files= [] #list of found files/sequences in nuke format
            #depth = 0 #reset current depth in the tree
            files= process_dir(walkPath, files= [], depth= 0)#this adds to 'files'
            #print 'walkPath=', walkPath, '\nfiles\n----\n'
            #highest common dir
            hcf= os.path.dirname(os.path.commonprefix(files))
            #del(task)
            #set task bar

            #discrete groups
            import itertools # better to do this earlier! Remember you have to sort the data before grouping -groupby method actually just iterates through a list and whenever the key changes it creates a new group. Be careful about having different sortDiscrete criteria to those which we sorted on!!!
            groupNodes= [] #group of similar nodes
            uniquekeys= [] #do i need?
            files.sort()
            #sortDiscrete= lambda filepath: os.path.dirname(filepath.split(hcf)[1]).split('/')[0]
            sortDiscrete= lambda filepath: os.path.dirname(filepath.split(hcf)[1]).split('/')[1]

            #print "\n".join([sortDiscrete(filepath) for filepath in files])
            for k, g in itertools.groupby(files, key= sortDiscrete):
                groupNodes.append(list(g))      # Store group iterator as a list
                uniquekeys.append(k)
                
                #print 'groups', groupNodes
                print(('uniquekeys', uniquekeys))

        

            task= nuke.ProgressTask('Loading files')
            gh= nuke.toNode("preferences")["GridHeight"].value()
            for j, g in enumerate(groupNodes):
                returnNodes= []

                for filepath in g:

                    if task.isCancelled():
                        break
                    # UPDATE PROGRESS BAR
                    task.setMessage( 'Loading file %s' % filepath )
                    task.setProgress( int( float(i) / float(len(walkPath))*100) )

                    print((j, filepath))
                    #fix windows paths
                    #filepath= file.replace("\\", "/")
                    #print file
                    #(nuke node, original filepath):
                    returnNodes.append(nuke_loader(filepath))
                nodes= [node for node in returnNodes if node is not None]
                if nodes:
                    label= uniquekeys[j]
                    if not label:
                        #just one group - take last dir
                        label= os.path.dirname(filepath)#.split('/')[-1]]                    
                    bd= backdrop_sd.make_backdrop(nodes, label= label)
                    [n.setXYpos(int(n.xpos()), int(n.ypos()+ (j*20*gh))) for n in nodes]
                    bd.setXYpos(int(bd.xpos()),int(bd.ypos()+ (j*20*gh)) )
                '''if exlist:
                    finalLabel= "Couldn't load\n"
                    for line in exlist:
                        finalLabel+= line+ '\n'
                    node= nuke.createNode('StickyNote')
                    node['label'].setValue(finalLabel)'''
                
            #call 'layout' on the resulting nodes
            #default = by last dir (backdrop it) then by class
            #but for now...
            #make new list
            del(task)
        
        #print 'returnNodes', returnNodes
        #print 'nodes',nodes
        if len(nodes)> 1: #  * AND IF EACH DIR HAS >1 items - how to do that?
            #should really sort by directories found in above code, but for now:
            #arrange_by_sd.arrange_by( nodes= nodes, sortKey= lambda node: node['file'].value().lower(), sortDiscrete= lambda node: node['file'].value().split(os.path.dirname(os.path.commonprefix([node['file'].value() for node in nodes])))[1].split('/')[1])  
            #arrange_by_sd.arrange_by( nodes= nodes, sortKey= lambda node: nuke.filename(node, nuke.REPLACE).lower(), sortDiscrete= lambda node: node['file'].value().split(os.path.dirname(os.path.commonprefix([node['file'].value() for node in nodes])))[1].split('/')[1])              
            '''print 'nodes', [nodes[0] for nodes in returnNodes]
            print 'sortKey', nodes[1].lower()
            print 'sortDiscrete', os.path.dirname(nodes[1].split(hcf)[1]).split('/')[0]
            arrange_by_sd.arrange_by( nodes= nodes, 
                sortKey= lambda node: nodes[1].lower(), 
                sortDiscrete= lambda node: os.path.dirname(nodes[1].split(hcf)[1]).split('/')[0])'''
        #return 
        #clear selected - in future I could check if we used 'potential_walkPaths'?
        if nodes:#- need to reset 'nodes'???
            [node.setSelected(False) for node in nuke.allNodes()]
            #print 11111
            #print [node for node in nodes]
            [node.setSelected(True) for node in nodes]
    else:
        return None
    

#then put most of this script in a def function and run layout on it.



if __name__ == "__main__":
    #runs when testing:
    recursive_read(walkPaths= None, maxdepth= -1)



'''
#recursive_read(r"Z:\Radiant_VFX\02_LiveProjects\2000_UCL_ChampionsLeague_2015-18\05_Dailies\Dailies_019__01-05-2014")
#recursive_read()
#recursive_read(r"Z:/Radiant_VFX/02_LiveProjects/2000_UCL_ChampionsLeague_2015-18/03_VFX/02_Dev/03_MAR/07_Maya/2000_UCL_titles_os-gs_shared/Cameras/")


#ask if we want to sort
#highlight duplicates
pass





###################################################################
###################################################################
###################################################################
######################################################################
############
#import fnmatch
#fnmatch.filter(['aaa','bb'], "*a")


def recursive_read(walkPath=''):

    def processFile(currentDir):
        #recursively process files within a directory
        # Get a list of files and Dirs in currentDir
        filesInCurDir = nuke.getFileNameList(os.path.normpath(currentDir))
 
        # Traverse through all files
        for file in filesInCurDir:
            curFile = os.path.join(currentDir, file)
 
            # Check if it's a normal file or directory
            if os.path.isdir(curFile):
                # Enter into directory for further processing
                processFile(curFile)
                #print "going into",curFile
            else:
                # Add to the file list
                files.append(curFile)
        #for i,file in enumerate(files):
        #    print i,file
        #print "curfile",curFile
        return files

    def nuke_loader(file):
        #load the right Class of object for given file
        classDict={}

    #main part of recursive load
    if not walkPath:
        walkPath=nuke.getClipname('Choose a file to load all files in this folder', multiple= False)
    try:
        if os.path.isfile(walkPath):
            walkPath=os.path.split(walkPath)[0]
    except:
        return
    if walkPath:
            print 'walkPath=',walkPath
            files=[]
            files=processFile(walkPath)
            print 'files\n----\n'
            for i,file in enumerate(files):
                print i,file
                nuke_loader(file)
    else:
        return
    

#add it to menu: Load all in dir = Shift+R
#nuke.menu( 'Nodes' ).addCommand("Image/Recursive Read...","recursive_read()","Shift+R")

recursive_read(r"Z:\Radiant_VFX\02_LiveProjects\2000_UCL_ChampionsLeague_2015-18\05_Dailies\Dailies_019__01-05-2014")
#recursive_read()
#recursive_read(r"Z:/Radiant_VFX/02_LiveProjects/2000_UCL_ChampionsLeague_2015-18/03_VFX/02_Dev/03_MAR/07_Maya/2000_UCL_titles_os-gs_shared/Cameras/")


print files
pass



##############################################################
#revised 'paste' function:
# - assume clipboard contains *something!*
# - try regular paste - anything?
# - multiple lines?
#then for each line:
# - try removing any spaces before each line
# - try expanding any regex
# - multiple diredctories to follow? ASK - add 'always follow' option
# - not just image files? Load everything then ASK... show counts/files and checkboxes
# - 
# - 
# - 
# - 
# - 
#########################################
# m_load_all_in_directory
# by Sean Danischevsky 2011, 2012
# recursively search a directory for Nuke loadable files
# and present them usefully!
# overview:
# - get dir, setup filters, prefs (or be passed these)
# - get list of dirs, check for files - done
# - check what extension
# - check with prefs what to do: 
# -           images: create seq, load seq, conv to stereo 
# -           geo: load geo
# -           camera: load camera
# -           else load into sticky note
#
#
# http://effbot.org/librarybook/os-path.htm

def recursive_read():
    import os, re, nuke
    verbose=True
    nameList=[]
    filesFound=[]
    ReadList=[]
    inStereo=True
    stereoReplace=[('_re_','_le_'),('/right/','/left/'),('_right_','_left_'),('_right-','_left-')] # (source,replace) for all right to left conversions needed to match paths and filenames





    def split_image_sequences(path, files):
      if verbose: print path
      #Get a list of unique names in file
      for i in files:
          sp=i.split('.')
          name=sp[0]
          ext=sp[-1]
          name2CheckFor=str(name)+'.'+str(ext)
          if name2CheckFor not in nameList:
              nameList.append(name2CheckFor)
      for n in nameList:
          curList=[]
          for i in files:
              if not str(path).endswith('/'):
                path+='/'#can this go outside loop?
              if verbose: print path
  
              if n.split('.')[0] in i:
                  if n.split('.')[-1] in i:
                      curList.append(path+i)
          if curList:
              filesFound.append(curList)
          filesFound.sort()
      return filesFound

    def imgSeq2NukeFormat(filesFound):
        for ff in filesFound:
          if verbose: print 'file found:', ff
          #SHOULDN'T NEED TO LOOP AS SHOULD BE A SORTED LIST BUT THIS IS FAILING FOR SOME REASON SO WORKING THROUGH LIST TO GET START AND END
          #UNCOMMENT THE NEXT 2 LINES AND COMMENT TO ###END MINMAX###
          #start=ff[0].split('.')[-2]
          #end=ff[-1].split('.')[-2]
          minMax=[]
          for i in ff:
              frames=i.split('.')[-2]
              minMax.append(frames)
          start=min(minMax)
          end=max(minMax)
          ###END MINMAX###
          if verbose: print 'start ', start, 'end ', end

          #move on and ignore if the file is a hidden file
          if  ff[0].split('/')[-1].startswith('.'):
            print 'hidden file skipped'
            continue     
          path=ff[0].split('/')[0]
          splitFiles= ff[0].split('.')
          name=splitFiles[0]


          padNum=splitFiles[-2]
          if padNum.isdigit():
              padding =len(splitFiles[-2])*'#'
          else:
              padding=''
          ext=splitFiles[-1]
      
          if padding:
              readFile=path+name+'.'+padding+'.'+ext+' '+start+'-'+end
          else:
              readFile=path+name+'.'+ext
          ReadList.append(readFile)
        return ReadList   

    def stereoMatch(fileName):
      #replace right strings with left strings to match paths and files
      for i in range(len(stereoReplace)):
        pattern = re.compile(stereoReplace[i][0])
        fileName = pattern.sub(stereoReplace[i][1], fileName)

      return fileName




    def createReads(ReadList):
      for r in ReadList:
          if r.split(' ')[0][-3:] not in ('obj', 'fbx','sfx'):
              if inStereo:
                 if '/re/' in r:
                    r_left=stereoMatch(r)
                    rnleft=nuke.createNode('Read')
                    rnright=nuke.createNode('Read')
                    jv=nuke.createNode('JoinViews')
                    rnleft['file'].fromUserText(r_left)
                    rnright['file'].fromUserText(r)
                    jv.setInput(0,rnleft)
                    jv.setInput(1,rnright)
                 elif '/le/' not in r:
                    rn=nuke.createNode('Read')
                    rn['file'].fromUserText(r)
              else:
                 rn=nuke.createNode('Read')
                 rn['file'].fromUserText(r)
          else:
              rn=nuke.createNode('ReadGeo')
              rn.setInput(0,None)
              rn['file'].fromUserText(r)
          #rn.setSelected(False)
          #createdNodes.append(rn)
      #for i in createdNodes: print i['file'].getValue()





    walkPath=nuke.getClipname('Choose Folder',multiple=False)
    if os.path.isfile(walkPath):walkPath=os.path.split(walkPath)[0]
    if verbose: print 'walkPath=',walkPath
    for i in os.walk(walkPath):
         filesFound=split_image_sequences(i[0], i[-1])
    if verbose: print 'files found ', filesFound
    readsList=imgSeq2NukeFormat(filesFound)
    if verbose: print 'readsList=', (readsList)
    createReads(readsList)
    #layout pls k thx bai
    return




#add it to menu: Load all in dir - Shift+R
#nuke.menu( 'Nodes' ).addCommand("Image/Recursive Read...","recursive_read()","Shift+R")
pass






############################
###########################
##########################


import os

def index(directory):
    # like os.listdir, but traverses directory trees
    stack = [directory]
    files = []
    while stack:
        directory = stack.pop()
        for file in os.listdir(directory):
            fullname = os.path.join(directory, file)
            files.append(fullname)
            if os.path.isdir(fullname) and not os.path.islink(fullname):
                stack.append(fullname)
    return files

#for file in index("/jobs/snowpiercer/gl_41"):
#    print file
############################

#walkPath="/jobs/snowpiercer/gl_41"
#walkPath="/jobs/snowpiercer/sc_32"
def walk(walkPath):
    filesFound=[]
    for path, dirs, files in os.walk(walkPath):
         if dirs: 
             for dir in dirs:
                 filesFound.append(os.path.join(path, dir))
    #for file in filesFound:
       # print file
    return filesFound


dirlist=walk(walkPath)
print dirlist
files=[]
for dir in dirlist:
    for read in nuke.getFileNameList(dir):
        fullRead=os.path.join(dir,read)
        if not os.path.isdir(fullRead):
            extension=fullRead.split('.')[-1]
            extension=extension.split(' ')[0]
            files.append((fullRead,extension))

print files
print len(files)  
    #need to sort/set now
    #sort the files 
# there dont seem to be any duplicates!
files = list(set(files))
files.sort() 
print len(files)  



    #define the types:
    def make_read(image):
        node=nuke.createNode('Read')
        node['file'].fromUserText('%s' % (image)) 
        return

    def make_stickynote(msg):
        filename = open(msg,"r")
        myLabel = filename.read(100)
        filename.close()
        finalLabel=("%s\n%s") % (msg,myLabel)
        node=nuke.createNode('StickyNote')
        node['label'].setValue(finalLabel)
        return

    def make_camera(msg):
        node=nuke.createNode('Camera2')
        #read_from_file
        node['file'].setValue(msg)
        node['label'].setValue(msg)
        return

    def make_readgeo(msg):
        node=nuke.createNode('ReadGeo2')
        #read_from_file
        node['file'].setValue(msg)
        node['label'].setValue(msg)
        return   

    #nodedir={'dpx':make_read,'db':make_stickynote}
    extRead=['dpx', 'exr','iff', 'jpg','mov','qt','png','tif','tiff']
    extCamera=['cam']#I think!
    extReadGeo=['fbx', 'obj']#fbx can contain objects as well as cameras... so load object
    extStickyNote=['xml','txt']

    #'xml' in extStickyNote
    extIgnore=[]
    #['ma', 'mel', 'meta','nk','nk~', 'pfcp', 'pfmp','rv', 'svn-base', 'svn/all-wcprops', 'svn/entries', 'swatches', 'tmp', 'vars', 'xmp', 'zip']
#now deal with the types:
exlist=[]
for file,extension in files:
    if extension in extRead:
        pass#make_read(file)
    elif extension in extStickyNote:
        pass#make_stickynote(file)
    elif extension in extCamera:
        pass#make_camera(file)
    elif extension in extReadGeo:
        make_readgeo(file)
    else:
     exlist.append(file)

if exlist:
    finalLabel="Couldn't load\n"
    for line in exlist:
        finalLabel+=line+'\n'
    node=nuke.createNode('StickyNote')
    node['label'].setValue(finalLabel)


#ask if we want to sort
#highlight duplicates
pass




###############################################################
#########################################
# m_load_all_in_directory
# 
#
#
#
# copy/ paste should access this script, esp if pasting a directory. It should ask "do you want to recursively load files?"
# then find the files
# then ask which we want to load (if there's more than one type).
#

def recursive_read():
    import os, re, nuke
    verbose=True
    nameList=[]
    filesFound=[]
    ReadList=[]
    inStereo=True
    stereoReplace=[('_re_','_le_'),(os.sep+'right'+os.sep,os.sep+'left'+os.sep),('_right_','_left_'),('_right-','_left-')] # (source,replace) for all right to left conversions needed to match paths and filenames





    def split_image_sequences(path, files):
      if verbose: print path
      #Get a list of unique names in file
      for i in files:
          sp=i.split('.')
          name=sp[0]
          ext=sp[-1]
          name2CheckFor=str(name)+'.'+str(ext)
          if name2CheckFor not in nameList:
              nameList.append(name2CheckFor)
      for n in nameList:
          curList=[]
          for i in files:
              if not str(path).endswith(os.sep):
                path+=os.sep#can this go outside loop?
              if verbose: print path
  
              if n.split('.')[0] in i:
                  if n.split('.')[-1] in i:
                      curList.append(path+i)
          if curList:
              filesFound.append(curList)
          filesFound.sort()
      return filesFound

    def imgSeq2NukeFormat(filesFound):
        for ff in filesFound:
          if verbose: print 'file found:', ff
          #SHOULDN'T NEED TO LOOP AS SHOULD BE A SORTED LIST BUT THIS IS FAILING FOR SOME REASON SO WORKING THROUGH LIST TO GET START AND END
          #UNCOMMENT THE NEXT 2 LINES AND COMMENT TO ###END MINMAX###
          #start=ff[0].split('.')[-2]
          #end=ff[-1].split('.')[-2]
          minMax=[]
          for i in ff:
              frames=i.split('.')[-2]
              minMax.append(frames)
          start=min(minMax)
          end=max(minMax)
          ###END MINMAX###
          if verbose:
              print 'start ', start, 'end ', end

          #move on and ignore if the file is a hidden file
          if ff[0].split(os.sep)[-1].startswith('.'):
              print 'hidden file skipped'
          #path=(ff[0].split(os.sep))[0]
          path=os.path.dirname(ff[0])
          print "path=", path
          splitFiles= ff[0].split('.')
          print "splitFiles=", splitFiles
          name=splitFiles[0]


          padNum=splitFiles[-2]
          if padNum.isdigit():
              padding =len(splitFiles[-2])*'#'
          else:
              padding=''
          ext=splitFiles[-1]
      
          if padding:
              readFile=path+name+'.'+padding+'.'+ext+' '+start+'-'+end
          else:
              readFile=path+name+'.'+ext
          ReadList.append(readFile)
        return ReadList   

    def stereoMatch(fileName):
      #replace right strings with left strings to match paths and files
      for i in range(len(stereoReplace)):
        pattern = re.compile(stereoReplace[i][0])
        fileName = pattern.sub(stereoReplace[i][1], fileName)

      return fileName

    def createReads(ReadList):
      for r in ReadList:
          if r.split(' ')[0][-3:] not in ('obj', 'fbx', 'sfx'):
              if inStereo:
                 if '%sre%s'%(os.sep,os.sep) in r:
                    r_left=stereoMatch(r)
                    rnleft=nuke.createNode('Read')
                    rnright=nuke.createNode('Read')
                    jv=nuke.createNode('JoinViews')
                    rnleft['file'].fromUserText(r_left)
                    rnright['file'].fromUserText(r)
                    jv.setInput(0,rnleft)
                    jv.setInput(1,rnright)
                 elif '%sle%s'%(os.sep,os.sep) not in r:
                    rn=nuke.createNode('Read')
                    rn['file'].fromUserText(r)
              else:
                 rn=nuke.createNode('Read')
                 rn['file'].fromUserText(r)
          else:
              rn=nuke.createNode('ReadGeo')
              rn.setInput(0,None)
              rn['file'].fromUserText(r)
          #rn.setSelected(False)
          #createdNodes.append(rn)
      #for i in createdNodes: print i['file'].getValue()





    walkPath=nuke.getClipname('Choose Folder', multiple= False)
    if os.path.isfile(walkPath):
        walkPath=os.path.split(walkPath)[0]
    if verbose:
        print 'walkPath=',walkPath
    for i in os.walk(walkPath):
         filesFound= split_image_sequences(i[0], i[-1])
    if verbose:
        print 'files found=', filesFound
    readsList=imgSeq2NukeFormat(filesFound)
    if verbose:
        print 'readsList=', readsList
    createReads(readsList)
    #layout pls k thx bai
    return


#add it to menu: Load all in dir = Shift+R
nuke.menu( 'Nodes' ).addCommand("Image/Recursive Read...","recursive_read()","Shift+R")


#EXAMPLES:
searchdir= "/mnt/projects/apw/edit/shots/"
for node in nuke.selectedNodes():
    recursive_read_sd.recursive_read(walkPaths= searchdir, maxdepth= 0, extRead= ['.mov'], includeString= os.path.basename(node['file'].value())[:11], excludeString= None, latest= False)

'''
pass












