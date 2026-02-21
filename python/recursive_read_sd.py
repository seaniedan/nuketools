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
import os
import re
import time
from collections import defaultdict

import backdrop_sd


def _natural_sort_key(s):
    """Key for natural sort so e.g. shot2, shot10, shot100 order correctly.
    Returns tuple of (type_order, value) so str and int are never compared."""
    if s is None:
        return ((0, ''),)
    parts = re.split(r'(\d+)', str(s).lower())
    out = []
    for x in parts:
        if not x:
            continue
        if x.isdigit():
            out.append((1, int(x)))
        else:
            out.append((0, x))
    return tuple(out) if out else ((0, ''),)


def _alphabetical_sort_key(s):
    """Key for simple case-insensitive alphabetical sort (for paths/files/classes)."""
    return (0, str(s).lower() if s is not None else '')


def recursive_read(walkPaths= None, maxdepth= -1, 
    extRead= ['.ari', '.avi', '.cin', '.dpx', '.dtex', '.exr', '.iff', '.gif', '.hdr', '.hdri', '.jpg', '.jpeg', '.mov', '.mp4' ,'.mxf', '.qt', '.pic', '.png', '.png16', '.psd', '.r3d', '.sgi', '.sgi16', '.rgb', '.rgba', '.tif', '.tiff', '.tif16', '.tiff16', '.ftif', '.ftiff', '.tga', '.targa', '.rla', '.yuv'], 
    extCamera= ['.cam'], extReadGeo= ['.abc', '.fbx', '.obj'], 
    extStickyNote= ['.csv', '.xml', '.txt', '.xpm'], 
    extOCIOFileTransform= ['.csp','.cms','.cube','.3dl','.blut','.vf','.cub','.cc'],
    extVectorfield= [],  # superseded by extOCIOFileTransform
    extOCIOCDLTransform= ['.ccc'],
    extParticleCache= ['.nkpc'],
    extIgnore= ['.autosave', '.dae', '.db', '.ifd', '.ma', '.mb', '.mel', '.meta', '.nk', '.nk~', '.nkple', '.gizmo', '.pkl', '.pickle', '.pfcp', '.pfmp', '.psb', '.rv', '.sc', '.svn-base', '.svn/all-wcprops', '.svn/entries', '.swatches', '.tmp', '.tx', '.vars', '.xmp', '.zip'],
    includeString= None, excludeString= None, latest= False, debug_path= None, timeout_seconds= 180):
    # timeout_seconds: stop after this many seconds (default 180). Set to None to disable.
    # More node types: see comment block below (ParticleCache, Precomp, etc.) or Nuke Nodes menu / Python API.
    # was     extVectorfield= ['.csp','.cms','.cube','.3dl','.blut','.vf','.cub'], 

    #walkPaths= a directory or list of directories (e.g. '/a/dir/' or ['/path/to/dir','/other/path'])
    #blacklist, whitelist: 
    #SHOULD do it like this:###################################################
    #nodedir= {'dpx': make_read, 
    #          'db': make_stickynote}  
    #for 'latest': only keep latest files.. in each dir/level?

    #can specify dict to use to replace this one, e.g. if you're only interested in dpx, {'dpx': 'Read'}
    import arrange_by_sd
    print(('walkPaths=', walkPaths))

    def build_tree(current_dir, root_path, depth):
        """Build a tree: {path, relative, files, subdirs}. Files and sibling dirs natural-sorted."""
        rel = os.path.relpath(current_dir, root_path).replace('\\', '/')
        if rel == '.':
            rel = ''
        files_in_cur = nuke.getFileNameList(os.path.abspath(current_dir))
        files = []
        subdirs = []
        if files_in_cur:
            for name in files_in_cur:
                # Only consider direct children: names with path separators belong in a subdir, not here
                if '/' in name or os.path.sep in name:
                    continue
                # Ignore dot files
                if name.startswith('.'):
                    continue
                cur = os.path.join(current_dir, name)
                if os.path.isdir(cur) or os.path.islink(cur):
                    if depth < maxdepth or maxdepth == -1:
                        print(("going into", cur))
                        subdirs.append(build_tree(cur, root_path, depth + 1))
                else:
                    files.append(cur)
        files.sort(key=_alphabetical_sort_key)
        subdirs.sort(key=lambda t: _alphabetical_sort_key(t['relative']))
        return {'path': current_dir, 'relative': rel, 'files': files, 'subdirs': subdirs}

    def _snap_to_grid(val, grid):
        """Snap value to grid (align down)."""
        return int(val // grid) * int(grid)

    def _node_file_extension(node):
        """File extension for layout grouping (e.g. '.exr', '.txt'). Fallback to class if no file."""
        try:
            v = node['file'].value()
            if v:
                return os.path.splitext(v)[1].lower() or node.Class()
        except Exception:
            pass
        # StickyNotes (e.g. .csv, .txt) have path in label first line
        try:
            label = node['label'].value()
            if label and '\n' in label:
                first_line = label.split('\n')[0].strip()
            else:
                first_line = label or ''
            if first_line and (first_line.startswith('/') or first_line.startswith(os.sep) or ':' in first_line or len(first_line) > 3):
                ext = os.path.splitext(first_line)[1].lower()
                if ext:
                    return ext
        except Exception:
            pass
        return node.Class()

    def layout_nodes_by_extension(nodes, start_x, start_y):
        """Place nodes in rows by file extension: one row per extension, left-to-right within row.
        Skips BackdropNode. Snaps to grid."""
        content = [n for n in nodes if n.Class() != 'BackdropNode']
        if not content:
            return
        gw = int(nuke.toNode("preferences")["GridWidth"].value())
        gh = int(nuke.toNode("preferences")["GridHeight"].value())
        by_ext = defaultdict(list)
        for n in content:
            by_ext[_node_file_extension(n)].append(n)
        def node_order(node):
            try:
                v = node['file'].value()
                return _alphabetical_sort_key(v) if v else _alphabetical_sort_key(node.name())
            except Exception:
                return _alphabetical_sort_key(node.name())
        row_y = _snap_to_grid(start_y, gh)
        for ext in sorted(by_ext.keys(), key=_alphabetical_sort_key):
            group = sorted(by_ext[ext], key=node_order)
            col_x = _snap_to_grid(start_x, gw)
            row_h = 0
            for n in group:
                n.setXYpos(col_x, row_y)
                row_h = max(row_h, n.screenHeight())
                col_x += _snap_to_grid(n.screenWidth() + gw, gw)
            row_y += _snap_to_grid(row_h + gh, gh)

    #define the types:
    def make_read(image):
        #node= nuke.createNode('Read')
        node= nuke.nodes.Read()#faster
        node['file'].fromUserText('%s' % (image))  #safest/easiest to do this way and not too slow.
        #node.setSelected(True) #I'll do this for all later
        return node

    def is_safe_file_path(file_path):
        """Validate that a file path is safe to read from"""
        if not file_path or not isinstance(file_path, str):
            return False
        
        # Normalize the path
        try:
            normalized_path = os.path.normpath(file_path)
        except:
            return False
        
        # Check for path traversal attempts
        if '..' in normalized_path:
            return False
        
        # Only allow reading from allowed file extensions
        allowed_extensions = ['.csv', '.xml', '.txt', '.xpm']
        _, ext = os.path.splitext(normalized_path.lower())
        if ext not in allowed_extensions:
            return False
        
        # Check if the file exists and is readable
        try:
            return os.path.isfile(normalized_path) and os.access(normalized_path, os.R_OK)
        except (OSError, IOError):
            return False

    def make_stickynote(msg):
        if not is_safe_file_path(msg):
            # If path is not safe, just create a sticky note with the filename
            finalLabel = os.path.basename(msg) if msg else "Invalid file path"
            node = nuke.createNode('StickyNote')
            node['label'].setValue(finalLabel)
            return node
        try:
            with open(msg, "r", encoding='utf-8', errors='ignore') as filename:
                myLabel = filename.read(100)
            finalLabel = ("%s\n%s") % (msg, myLabel)
            node = nuke.createNode('StickyNote')
            node['label'].setValue(finalLabel)
            return node
        except (IOError, OSError, Exception) as e:
            # If file reading fails, create a sticky note with error info
            finalLabel = ("%s\nError reading file: %s") % (msg, str(e))
            node = nuke.createNode('StickyNote')
            node['label'].setValue(finalLabel)
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
        # OCIO LUT / file transform (.cube, .cc, .csp, etc.)
        node = nuke.nodes.OCIOFileTransform(file=file)
        return node        

    def make_OCIOCDLTransform(file):
        # Open Color In Out Color Decision List (.ccc)
        node = nuke.nodes.OCIOCDLTransform(file=file, read_from_file=True)
        return node

    def make_ParticleCache(file):
        node = nuke.nodes.ParticleCache()
        node['file'].fromUserText('%s' % (file))
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
                            return make_OCIOFileTransform(file)
                        elif extension in extVectorfield:
                            return make_vectorfield(file)
                        elif extension in extOCIOCDLTransform:
                            return make_OCIOCDLTransform(file)
                        elif extension in extParticleCache:
                            return make_ParticleCache(file)
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
            walkPaths = [walkPaths]

        gw = int(nuke.toNode("preferences")["GridWidth"].value())
        gh = int(nuke.toNode("preferences")["GridHeight"].value())
        bd_pad = max(gw * 2, gh * 2)
        all_created_nodes = []
        start_time = time.time()

        def depth_first_list(tree):
            """Depth-first order: parent before children (for pass 2 nesting)."""
            out = [tree]
            for sub in tree['subdirs']:
                out.extend(depth_first_list(sub))
            return out

        def breadth_first_list(tree):
            """Breadth-first order: root, then all immediate subdirs, then their subdirs, etc.
            So files (root) appear first, then subdirectories below."""
            out = []
            level = [tree]
            while level:
                out.extend(level)
                level = [sub for node in level for sub in node.get('subdirs') or []]
            return out

        next_base_x = 0
        root_gap = int(max(gw * 6, bd_pad * 2))  # horizontal gap between multiple roots

        for root_index, walkPath in enumerate(sorted(set(walkPaths), key=_alphabetical_sort_key)):
            if timeout_seconds is not None and (time.time() - start_time) > timeout_seconds:
                break
            if not os.path.isdir(walkPath):
                continue
            task = nuke.ProgressTask('Building directory tree')
            task.setMessage('Scanning %s' % walkPath)
            tree = build_tree(walkPath, walkPath, 0)
            df = depth_first_list(tree)
            total_dirs = len(df)
            if total_dirs == 0:
                continue

            side_pad = int(gw * 2)
            base_x = next_base_x
            base_y = 0

            def layout_recursive(node, start_x, start_y, dfs_index_ref):
                """Place file nodes only: layout by extension, then recurse into subdirs (each below the previous). Returns end_y."""
                rel = node.get('relative') or ''
                if task.isCancelled():
                    return start_y
                idx = dfs_index_ref[0]
                dfs_index_ref[0] += 1
                task.setMessage('Layout %s (%d/%d)' % (rel or '(root)', idx + 1, total_dirs))
                task.setProgress(int(100.0 * (idx + 1) / total_dirs))

                files_here = (node.get('files') or [])[:]
                files_here.sort(key=_alphabetical_sort_key)
                returnNodes = []
                for filepath in files_here:
                    returnNodes.append(nuke_loader(filepath))
                nodes_here = [n for n in returnNodes if n is not None]
                node['nodes'] = nodes_here
                all_created_nodes.extend(nodes_here)

                if nodes_here:
                    layout_nodes_by_extension(nodes_here, start_x, start_y)
                    block_bottom = max(n.ypos() + n.screenHeight() for n in nodes_here)
                    start_y = block_bottom + bd_pad

                for sub in node.get('subdirs') or []:
                    start_y = layout_recursive(sub, start_x + side_pad, start_y, dfs_index_ref) + bd_pad

                return start_y

            # 1) Layout: place all file nodes (no backdrops yet)
            task.setMessage('Layout (files only)')
            layout_recursive(tree, base_x, base_y, [0])

            # Optional debug file (after layout, before backdrops)
            if debug_path:
                try:
                    with open(debug_path, 'w') as f:
                        f.write('recursive_read_sd debug (after layout, before backdrops)\n')
                        f.write('walkPath: %s\n\n' % walkPath)
                        f.write('Depth-first: each dir with its files\n')
                        f.write('%s\n' % ('-' * 80))
                        for idx, node in enumerate(df):
                            rel = node['relative'] or '(root)'
                            files_here = node.get('files') or []
                            nodes_here = node.get('nodes') or []
                            f.write('\n[%d] relative: %s  nodes: %d\n' % (idx, rel, len(nodes_here)))
                            for fi, fp in enumerate(files_here[:50]):
                                f.write('      [%d] %s\n' % (fi, os.path.relpath(fp, walkPath).replace('\\', '/')))
                            if len(files_here) > 50:
                                f.write('      ... and %d more\n' % (len(files_here) - 50))
                        f.write('\n%s\n' % ('-' * 80))
                except Exception as e:
                    print('recursive_read_sd debug write failed: %s' % e)

            # 2) Create all backdrops at the end (reverse depth-first: children first, then parent contains them)
            node_to_dfs_idx = {id(n): i for i, n in enumerate(df)}

            def create_backdrops_reverse_dfs(node):
                for sub in node.get('subdirs') or []:
                    create_backdrops_reverse_dfs(sub)
                contents = list(node.get('nodes') or [])
                for sub in node.get('subdirs') or []:
                    if sub.get('backdrop'):
                        contents.append(sub['backdrop'])
                if not contents:
                    node['backdrop'] = None
                    return
                rel = node.get('relative') or ''
                label = os.path.abspath(walkPath) if rel == '' else rel
                if debug_path:
                    idx = node_to_dfs_idx.get(id(node), -1)
                    label = '[%d] %s' % (idx, label)
                bd = backdrop_sd.make_backdrop(contents, label=label, fix_depth=False, cover_backdrops=True)
                node['backdrop'] = bd

            task.setMessage('Creating backdrops')
            create_backdrops_reverse_dfs(tree)

            # 3) Z-order: assign in depth-first order so root=0 (back), deeper=higher z (on top).
            # That way the larger parent backdrop is behind the smaller child backdrops it contains.
            def assign_z_order(node, z_list):
                if node.get('backdrop'):
                    z_list.append(node['backdrop'])
                for sub in node.get('subdirs') or []:
                    assign_z_order(sub, z_list)

            backdrops_dfs = []
            assign_z_order(tree, backdrops_dfs)
            for z, bd in enumerate(backdrops_dfs):
                try:
                    bd.knob('z_order').setValue(z)
                except Exception:
                    pass

            # 4) Optional: resize root backdrop to contain full tree
            def all_items_in_tree(t):
                out = list(t.get('nodes') or [])
                if t.get('backdrop'):
                    out.append(t['backdrop'])
                for sub in t.get('subdirs') or []:
                    out.extend(all_items_in_tree(sub))
                return out

            root_node = df[0]
            all_items = all_items_in_tree(tree)
            if all_items and root_node.get('backdrop'):
                min_x = min(n.xpos() for n in all_items)
                min_y = min(n.ypos() for n in all_items)
                max_x = max(n.xpos() + n.screenWidth() for n in all_items)
                max_y = max(n.ypos() + n.screenHeight() for n in all_items)
                outer_pad = int(max(gw * 3, gh * 3))
                root_bd = root_node['backdrop']
                root_bd.setXYpos(int(min_x - outer_pad), int(min_y - outer_pad))
                root_bd['bdwidth'].setValue(int(max_x - min_x + 2 * outer_pad))
                root_bd['bdheight'].setValue(int(max_y - min_y + 2 * outer_pad))

            # So next root starts to the right of this one with a clear gap
            if all_items:
                next_base_x = max(n.xpos() + n.screenWidth() for n in all_items) + root_gap

            del task

        if all_created_nodes:
            for n in nuke.allNodes():
                n.setSelected(False)
            for n in all_created_nodes:
                n.setSelected(True)
    else:
        return None
    

#then put most of this script in a def function and run layout on it.



if __name__ == "__main__":
    recursive_read(walkPaths=None, maxdepth=-1)

# Run from Nuke's script editor (reload after editing):
#   import importlib
#   import recursive_read_sd
#   importlib.reload(recursive_read_sd)
#   recursive_read_sd.recursive_read()
#
# Temporary debug file (see which dir each file is assigned to, after pass 1):
#   recursive_read_sd.recursive_read(debug_path='/tmp/recursive_read_debug.txt')










