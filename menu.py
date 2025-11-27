# Sean Danischevsky NukeTools menu.py

import nuke
import os

# Add PluginPaths to tools and icons
nuke.pluginAddPath(('gizmos', 'groups', 'python', 'icons', 'images', 'ToolSets'))

#menu naming
SDNUKETOOLS="SDNukeTools"
sdnuketools_node_menu = nuke.menu('Nodes').addMenu(SDNUKETOOLS, icon="SeanScripts.png")



####################################################
# These items always run

# Add Gizmos and Groups to Nodes/SDNukeTools menu
import sanitize_gizmos
import load_gizmos
print("Loading seaniedan nuketools gizmos.")
try:
    stats = load_gizmos.load_gizmos(node_menu=sdnuketools_node_menu)
    if stats is not None:
        print(f"Gizmo loading complete: {stats['loaded_gizmos']} gizmos loaded")
    else:
        print("Gizmo loading complete: No gizmos found or error occurred")
except Exception as e:
    print(f"Error loading gizmos: {e}")
    print("Gizmo loading complete: Error occurred")

# Add load test image functions to SDNukeTools node menu
sdnuketools_node_menu.addCommand("Draw/Load/Kodak Digital Laboratory Aim Density (LAD) Test Image (2K)",
    "import load_test_image_sd; load_test_image_sd.load_test_image()", icon="Read.png")

sdnuketools_node_menu.addCommand("Draw/Load/Kodak Digital Laboratory Aim Density (LAD) Test Image (4K)",
    "import load_test_image_sd; load_test_image_sd.load_test_image_4k()", icon="Read.png")

# add useful autolabels
import autolabel_sd

# fix unnecessary warnings when deleting nodes
import delete_sd

# give info for multiple nodes, detailed info on files
import multiple_node_info_sd

# mass node changes
import MassivePanel

# improved search and replace panel
import SearchReplacePanel

# Node defaults
import node_defaults

# add animated snap to axis menu
import animatedSnap3D


# Zoom to centre of Nuke DAG (@ adds python script with no menu item)
nuke.menu("Nuke").addCommand("@;Zoom to 1_sd", 
    "import zoom_to_1_sd; zoom_to_1_sd.zoom_to_1_sd()", "h", shortcutContext= dagContext)

#swap A-B inputs should work for all selected nodes:
nuke.menu('Nuke').findItem('Edit').findItem('Node').addCommand("Swap A - B", 
    "[nukescripts.swapAB(node) for node in nuke.selectedNodes()]", "+X", shortcutContext= dagContext)

nuke.menu('Nuke').findItem('Edit').findItem('Node').addCommand( "Toggle Disable", 
    "import toggle_disable_sd; toggle_disable_sd.toggleDisable(nuke.selectedNodes())", "Alt+Shift+d", shortcutContext= dagContext) 

#color backdrops automatically based on first line of text. Keep this line:
import backdrop_sd
# But comment this out if you don't want to color backdrops automatically based on first line of text
nuke.addKnobChanged(backdrop_sd.autocolor_bd, nodeClass= "BackdropNode")

#autosaves
import autosave_sd
nuke.addOnScriptSave(autosave_sd.autosave_sd)


#AUTOWRITE/MAKE WRITE DIRECTORIES
#Slightly redundant as Nuke10+ has 'create_directories' option,
#HOWEVER, it doesn't have it for ['SmartVector', 'WriteGeo', 'GenerateLUT'] nodes. 
#add for GenerateLUT, SmartVector and WriteGeo nodes: 
import make_write_directories_sd
for nodeClass in ['SmartVector', 'WriteGeo', 'GenerateLUT', 'Write']:
    nuke.addBeforeRender(make_write_directories_sd.write_mkdir, nodeClass= nodeClass) 
del(nodeClass)
    
####################################################
####################################################
#Nuke Menu
#File, Edit, Workspace, Viewer, Render, Cache, Help .... SDNukeTools


#File Menu
file_menu = nuke.menu('Nuke').findItem('File')

# Nuke x <-> regular Nuke switcher
if nuke.env['nukex']:
    # we're in NukeX. Add ability to release licence and reload script in regular Nuke:
    file_menu.addCommand("Jump to regular Nuke", "import launch_nukeX;launch_nukeX.launchNukeX(x=False)")
else:
    # we're in regular Nuke. Add ability to reload script in NukeX:
    file_menu.addCommand("Jump to NukeX", "import launch_nukeX;launch_nukeX.launchNukeX(x=True)")

file_menu.addCommand("Collect Files",
        "import collectFiles;collectFiles.collectFiles()")

del(file_menu)


# Nuke -> Edit Menu
edit_menu = nuke.menu('Nuke').findItem('Edit')

# Nothing Real/Apple Shake style 'one-way' clone
edit_menu.addCommand('Shake style one-way clone',
    "import shake_style_clone; shake_style_clone.shakeClone(nodes= nuke.selectedNodes())", "ctrl+k", shortcutContext= dagContext)

# tween nodes
edit_menu.addCommand('Tween nodes',
    "import tween_nodes_sd; tween_nodes_sd.tween_nodes(nodes= nuke.selectedNodes())")

# paste multiple
edit_menu.addCommand("Paste Multiple",
    "import paste_multiple_sd; paste_multiple_sd.paste_multiple()", 'alt+v',
    shortcutContext= dagContext)

edit_menu.addCommand( "Select Upstream Nodes and backdrops",
        "import script_clean_sd; script_clean_sd.select_upstream_sd(nuke.selectedNodes())", 'shift+d', shortcutContext= dagContext)

#Sort selection order of nodes, from left to right
edit_menu.addCommand( "Sort Selection Order (left to right)", 
        "import select_left_to_right_sd; select_left_to_right_sd.select_left_to_right(nuke.selectedNodes())")

#delete errored nodes
edit_menu.addCommand("Script/Delete all errored nodes",
    "import script_clean_sd; script_clean_sd.delete_all_errored_nodes(nuke.selectedNodes() or nuke.allNodes())")

#cleanup script
edit_menu.addCommand("Script/Cleanup script",
    "import script_clean_sd; script_clean_sd.cleanupScript(nuke.selectedNodes())")

edit_menu.addCommand( "Script/Tidy selected nodes",
    "import script_clean_sd; script_clean_sd.tidy(nuke.selectedNodes())")

edit_menu.addCommand( "Script/Show Tidyness",
    "import tidyness_sd; tidyness_sd.show_tidyness(nuke.selectedNodes() or nuke.allNodes())")


#Select Similar Class nodes
edit_menu.findItem('Select Similar').addCommand('Class',
    "nuke.selectSimilar(nuke.MATCH_CLASS)", 'shift+c', shortcutContext= dagContext)

#CTRL + to increase font size
edit_menu.addCommand('Font Size/Increase',
    "import adjust_font_sizes_sd; adjust_font_sizes_sd.adjust_font_sizes(1)", 'ctrl+=')

#CTRL - to decrease font size
edit_menu.addCommand('Font Size/Decrease',
    "import adjust_font_sizes_sd; adjust_font_sizes_sd.adjust_font_sizes(-1)", 'ctrl+-')

del(edit_menu)

# Nuke -> Edit -> Node Menu 
edit_node_menu = nuke.menu('Nuke').findItem('Edit').findItem('Node')

# Arrange by
edit_node_menu.addCommand("Arrange by...",
    "import arrange_by_sd; arrange_by_sd.arrange_by(nuke.selectedNodes())", "Shift+L", shortcutContext= dagContext)

# Stitch
edit_node_menu.addCommand("Stitch",
        "import stitch_sd; stitch_sd.stitch_sd(nuke.selectedNodes('Read'))")



#add dot input
edit_node_menu.addCommand("Make Dot Input",
    "import make_dot_input_sd; make_dot_input_sd.make_dot_input(nuke.selectedNodes())", "alt+d",
    shortcutContext= dagContext)

edit_node_menu.addCommand( "Select Downstream Nodes (and backdrops)",
        "import script_clean_sd; script_clean_sd.select_downstream(nuke.selectedNodes())", 'alt+shift+d', shortcutContext= dagContext)



# Translate/Scale/Rotate nodes
# Translate nodes
edit_node_menu.addCommand('Translate/Left',
    "import move_nodes_sd; move_nodes_sd.translate_nodes_left(nuke.selectedNodes())", 'shift+left', shortcutContext= dagContext)
edit_node_menu.addCommand('Translate/Right',
    "import move_nodes_sd; move_nodes_sd.translate_nodes_right(nuke.selectedNodes())", 'shift+right', shortcutContext= dagContext)
edit_node_menu.addCommand('Translate/Up',
    "import move_nodes_sd; move_nodes_sd.translate_nodes_up(nuke.selectedNodes())", 'shift+up', shortcutContext= dagContext)
edit_node_menu.addCommand('Translate/Down',
    "import move_nodes_sd; move_nodes_sd.translate_nodes_down(nuke.selectedNodes())", 'shift+down', shortcutContext= dagContext)

#scale nodes
edit_node_menu.addCommand('Scale/Down in x and y',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes() or nuke.allNodes(), .9, .9)", 'shift+alt+-', shortcutContext= dagContext)
edit_node_menu.addCommand('Scale/Up in x and y',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes(), 1.1, 1.1)", 'shift+alt++', shortcutContext= dagContext)

edit_node_menu.addCommand('Scale/Down in x',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes() or nuke.allNodes(), .9, 1)", 'alt+-', shortcutContext= dagContext)
edit_node_menu.addCommand('Scale/Up in x',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes() or nuke.allNodes(), 1.1, 1)", 'alt+=', shortcutContext= dagContext)
edit_node_menu.addCommand('Scale/Down in y',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes() or nuke.allNodes(), 1, .9)", 'shift+-', shortcutContext= dagContext)
edit_node_menu.addCommand('Scale/Up in y',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes() or nuke.allNodes(), 1, 1.1)", 'shift++', shortcutContext= dagContext)

edit_node_menu.addCommand('Scale/Mirror Vertical (flip)',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes(), 1, -1)")
edit_node_menu.addCommand('Scale/Mirror Horizontal (flop)',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes(), -1, 1)")



#Rotate nodes
edit_node_menu.addCommand('Rotate/Clockwise',
    "import move_nodes_sd; move_nodes_sd.rotate_nodes_clockwise(nuke.selectedNodes() or nuke.allNodes())")
edit_node_menu.addCommand('Rotate/Anticlockwise',
    "import move_nodes_sd; move_nodes_sd.rotate_nodes_anticlockwise(nuke.selectedNodes() or nuke.allNodes())")

edit_node_menu.addCommand('Rotate/Ask',
    "import move_nodes_sd; move_nodes_sd.rotate_nodes_arbitrary(nuke.selectedNodes() or nuke.allNodes())")

#align nodes
edit_node_menu.addCommand('Align/in x',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes() or nuke.allNodes(), 0, 1)", 'alt+x', shortcutContext= dagContext)
edit_node_menu.addCommand('Align/in y',
    "import move_nodes_sd; move_nodes_sd.scale_nodes(nuke.selectedNodes() or nuke.allNodes(), 1, 0)", 'alt+y', shortcutContext= dagContext)

# copy paths
edit_node_menu.addCommand("Filename/Copy Paths to Clipboard",
    "import copy_file_to_clipboard_sd; copy_file_to_clipboard_sd.copy_text_to_clipboard(nodes= nuke.selectedNodes())", "Alt+c", shortcutContext= dagContext)

# open in browser
edit_node_menu.addCommand("Filename/Open Directories in Browser",
    "import copy_file_to_clipboard_sd; copy_file_to_clipboard_sd.open_dirs_in_browser(nuke.selectedNodes())", "Shift+o", shortcutContext= dagContext)


del(edit_node_menu)




#Viewer menu
# Add handles commands to the Viewer Menu

viewer_menu = nuke.menu('Nuke').findItem('Viewer')
viewer_menu.addCommand('Set Viewer Handles/0 frames',
    "import set_viewer_handles; set_viewer_handles.set_viewer_range(0, 0)")
viewer_menu.addCommand('Set Viewer Handles/8 frames',
    "import set_viewer_handles; set_viewer_handles.set_viewer_range(8, 8)")
viewer_menu.addCommand('Set Viewer Handles/10 frames',
    "import set_viewer_handles; set_viewer_handles.set_viewer_range(10, 10)")
viewer_menu.addCommand('Set Viewer Handles/12 frames',
    "import set_viewer_handles; set_viewer_handles.set_viewer_range(12, 12)")
viewer_menu.addCommand('Set Viewer Handles/16 frames',
    "import set_viewer_handles; set_viewer_handles.set_viewer_range(16, 16)")
viewer_menu.addCommand('Set Viewer Handles/48 frames',
    "import set_viewer_handles; set_viewer_handles.set_viewer_range(48, 48)")
viewer_menu.addCommand('Set Viewer Handles/ask',
    "import set_viewer_handles; set_viewer_handles.set_viewer_range(ask= True)")


# Add screengrab snapshot command to the Viewer Menu
viewer_menu.addCommand('Screengrab Viewer',
    "import screengrab_viewer_sd; screengrab_viewer_sd.capture_viewer()")

del(viewer_menu)



#Render menu

render_menu = nuke.menu('Nuke').findItem('Render')
render_menu.addCommand("Convert to EXR",
    "import convert_to_exr_sd; convert_to_exr_sd.convert_to_exr(nuke.selectedNodes('Read'))" )

render_menu.addCommand("Copy files instead of rendering",
    "import copy_instead_of_render_sd;\
    copy_instead_of_render_sd.copy_instead_of_render(destNodes= nuke.selectedNodes())","")

render_menu.addCommand("Copy list of missing frames from selected Read or Write nodes",
    "import sequence_check_sd; sequence_check_sd.list_missing_frames(nuke.selectedNodes('Read')+ nuke.selectedNodes('Write')+ nuke.selectedNodes('WriteTank'))", "")

render_menu.addCommand("Make Thumbnails",
    "import thumbnails_sd; thumbnails_sd.make_thumbnails(nuke.selectedNodes())")


render_menu.addCommand("Copy Command Line Render Command",
    "import copy_command_line_render_command_sd;\
    copy_command_line_render_command_sd.copy_command_line_render_command_to_clipboard()")

render_menu.addCommand("Render Selected one after the other",
    "import render_one_after_the_other_sd;\
    render_one_after_the_other_sd.renderSelected(nuke.selectedNodes())", "")

render_menu.addCommand("Copy Roto or RotoPaint frame range to clipboard",
    "import copy_rotopaint_range_sd;\
    copy_rotopaint_range_sd.get_rotopaint_range(nodes= nuke.selectedNodes('RotoPaint')+ nuke.selectedNodes('Roto'))")

render_menu.addCommand("Set Write render ranges to input and copy maximum frame range to clipboard",
    "import copy_write_range_sd;\
    copy_write_range_sd.set_write_range(nodes= nuke.selectedNodes('Write')+ nuke.selectedNodes('WriteTank'))")

#render range tools - split on gaps etc to render first then last frames
render_menu.addCommand("Copy Render Range: on tens", "import render_range_sd; render_range_sd.split_range_tens()")
render_menu.addCommand("Copy Render Range: fill gaps", "import render_range_sd; render_range_sd.split_range_gaps()")

del(render_menu)


######################
#Cache menu

## access Performance Timers
cache_menu = nuke.menu('Nuke').findItem('Cache')
cache_menu.addCommand ("Performance Timers/Start", "nuke.startPerformanceTimers()")
cache_menu.addCommand ("Performance Timers/Reset", "nuke.resetPerformanceTimers()")
cache_menu.addCommand ("Performance Timers/Stop", "nuke.stopPerformanceTimers()")
del(cache_menu)


######################
#create SDNukeTools menu 
sdnuketools_menu= nuke.menu('Nuke').addMenu(SDNUKETOOLS)

#backdrops tools
sdnuketools_menu.addCommand("Backdrop/Reformat Backdrop Nodes",#replaced by changing shift+a version
    "import backdrop_sd; backdrop_sd.reformat_backdrops(nuke.selectedNodes('BackdropNode'))")
sdnuketools_menu.addCommand("Backdrop/Scan Nodes for Backdrop collection",
    "backdrop_sd.scan_nodes_for_collection(nuke.selectedNodes())")
sdnuketools_menu.addCommand("Backdrop/Show Backdrop collection",
    "backdrop_sd.show_collection_as_backdrops()")

#create message or image in the nodegraph
sdnuketools_menu.addCommand("Other/Create message or image in the Node Graph",
    "import write_name_in_dag_sd;write_name_in_dag_sd.write_name_or_image_in_dag()")

#split exrs
sdnuketools_menu.addCommand('Read/Split EXR channels',
    'import split_exrs_sd;split_exrs_sd.split_exrs()')

#pick best track
sdnuketools_menu.addCommand("Transform/Pick Best Track",
    "import tracker_median_sd; tracker_median_sd.tracker_median_sd()" )

#copy animation on this frame - WIP
sdnuketools_menu.addCommand("Transform/Copy Animation Curves on this Frame (WIP)",
    "import copy_animation_curves_on_this_frame_sd;\
    curve_dict= copy_animation_curves_on_this_frame_sd.setup(nuke.selectedNodes());copy_animation_curves_on_this_frame_sd.copy_values_to_keyframe(curve_dict, nuke.frame())" )

#smooth Camera
sdnuketools_menu.addCommand("3d/Smooth Selected Cameras",
    "import create_smooth_camera; create_smooth_camera.main(nuke.selectedNodes())")

#smart cornerpin, mocha tracker
sdnuketools_menu.addCommand("Transform/Convert Cornerpin to smart Cornerpin or MochaTracker to Tracker",
    "import convert_CornerPin_to_Smart_CornerPin_sd;\
    convert_CornerPin_to_Smart_CornerPin_sd.fix_mocha_tracker_or_cornerpin(nuke.selectedNodes())")

#Search keyboard shortcuts 
sdnuketools_menu.addCommand("Other/Search Keyboard Shortcuts",
    "import search_keyboard_shortcuts;\
    nuke.display('search_keyboard_shortcuts.search_keyboard_shortcuts()', None, title = 'Nuke key assignments')")

#Reload files in Read, ReadGeo, OCIOCDLTransforms etc
sdnuketools_menu.addCommand("Read/Reload Files",
    "[node['reload'].execute() for node in nuke.selectedNodes() or nuke.allNodes() if 'reload' in node.knobs().keys()]")


sdnuketools_menu.addCommand("Read/Layout Reads by Sequence",
    "import arrange_by_sd;\
    arrange_by_sd.arrange_by(nuke.selectedNodes('Read'), sortKey= lambda node: nuke.filename(node, nuke.REPLACE).lower(), sortDiscrete= lambda node: '_'.join(    os.path.basename(node['file'].value()) .split('_') [:3]  )  )")

sdnuketools_menu.addCommand("3d/Create Camera from Metadata",
    "import create_camera_from_metadata_sd;\
    create_camera_from_metadata_sd.createMetaDatCam(nuke.selectedNode())")

#split sequences to multiple Read nodes
sdnuketools_menu.addCommand('Read/Split Read sequence to multiple single Reads', 
    "import split_to_frames_sd;\
    split_to_frames_sd.split_to_frames(nodes= nuke.selectedNodes('Read'))")

#split sequences to Frameholds with Postage stamps
sdnuketools_menu.addCommand('Read/Split Read sequence to Frameholds with Postage stamps', 
    "import split_to_frames_sd;\
    split_to_frames_sd.split_to_frameholds(nodes= nuke.selectedNodes('Read'))")

#set root frame range to selected reads
sdnuketools_menu.addCommand("Read/Set Frame Range to selected (or all) Reads",
    "import set_frame_range_to_selected_sd; set_frame_range_to_selected_sd.set_frame_range_to_selected(nuke.selectedNodes('Read') or nuke.allNodes('Read'))")


#Compare Selected
sdnuketools_menu.addCommand("Other/Compare Selected",
    "import stitch_sd; stitch_sd.stitch_check_sd(nuke.selectedNodes())")

#Compare sequences - execute selected Compared_sd nodes
sdnuketools_menu.addCommand("Other/Analyse Input Sequences on selected Compare_sd Nodes",
    "[node['comparesequence'].execute() for node in nuke.selectedNodes('Group')]")

#autocrop
sdnuketools_menu.addCommand("Transform/Put auto-crop after selected node", 
    "import nukescripts; nukescripts.autocrop(first= None, last= None, inc= None, layer= 'rgba')")
sdnuketools_menu.addCommand("Transform/Put un-crop after selected Crop node", 
    "import uncrop_sd; uncrop_sd.uncrop()")

#print environment variables
sdnuketools_menu.addCommand("Python/Print Environment Variables", 
    "import print_environment_variables_sd; print_environment_variables_sd.print_environment_variables()")

#print nuke paths
sdnuketools_menu.addCommand("Python/Print Nuke Paths", 
    "import print_nuke_paths_sd; print_nuke_paths_sd.print_nuke_paths()")

#print python modules
sdnuketools_menu.addCommand("Python/Print Python Modules", 
    "import print_python_modules_sd; print_python_modules_sd.print_python_modules()")

# Add sanitize gizmo tool to SDNukeTools menu
sdnuketools_menu.addCommand("Python/Sanitize Gizmos", 
    "import sanitize_gizmos; sanitize_gizmos.sanitize_gizmos_unified()")

# Add fix nuke script tool to SDNukeTools menu
sdnuketools_menu.addCommand("Python/Fix Nuke Script", 
    "import fix_nuke_script; fix_nuke_script.main()")

#end
del(sdnuketools_menu)
#####################################################################################


#Nodes menu

#Image

#Recursive Read
nuke.menu('Nodes').findItem('Image').addCommand("Recursive Read...",
    "import recursive_read_sd; recursive_read_sd.recursive_read()", "Alt+R", shortcutContext= dagContext)

#Read from Write - not needed at Automatik
nuke.menu('Nodes').findItem('Image').addCommand("Read from Write",
    "import read_from_write_sd; read_from_write_sd.readFromWrites(nuke.selectedNodes())", "Shift+R", shortcutContext= dagContext)


#st map create
nuke.menu('Nodes').findItem('Draw').addCommand("STMap Create",
    "import stmap_create_sd; stmap_create_sd.stmap_create()", icon="Ramp.png")

#Other
#backdrop
nuke.toolbar("Nodes").findItem("Other").addCommand("Smart Backdrop",
        "backdrop_sd.make_backdrop(nuke.selectedNodes())", "Shift+a", shortcutContext= dagContext)


#####################################################################################

# Animation menu

nuke.menu('Animation').addMenu(SDNUKETOOLS).addCommand('Copy keyframes to frame list', 
    "import copy_frame_list_to_clipboard_sd;copy_frame_list_to_clipboard_sd.copy_framelist()" )


#####################################################################################
#####################################################################################


##########################
#create better defaults for ramp
def create_ramp():
    ramp= nuke.createNode("Ramp")
    if ramp.inputs():
        ramp['p0'].setValue([0, 0])
        ramp['p1'].setValue([0, ramp.height()])
        ramp['replace'].setValue(1)
    else:
        ramp['p0'].setValue([0, 0])
        ramp['p1'].setValue([ramp.width(), 0])

nuke.toolbar("Nodes").addMenu("Draw", "ToolbarDraw.png").addCommand("Ramp",
    "create_ramp()", icon= "Ramp.png")


###########################
def create_radial():
    #make spherical radial nodes
    #to fit screen
    #by Sean Danischevsky 2014
    #to do: check aspect ratio - currently assumes aspect ratio 1
    #shift + ctrl Radial corners to keep aspect.

    r= nuke.createNode('Radial')
    #alternative code to make radius 
    #pointA = nuke.math.Vector2(0,0)
    #pointB = nuke.math.Vector2(r.width(), r.height())
    #rad = pointA.distanceBetween(pointB)/2.0
    rad= min (r.width(), r.height())

    xoffset= (r.width()- rad)/ 2.0
    yoffset= (r.height()- rad)/ 2.0
    r['area'].setValue((xoffset, yoffset, rad+ xoffset, rad+ yoffset))

nuke.toolbar("Nodes").addMenu("Draw", "ToolbarDraw.png").addCommand("Radial",
    "create_radial()", icon= "Radial.png") 




##########################
#create better defaults for LayerContactSheet
def create_layerContactSheet():
    lcr = nuke.createNode("LayerContactSheet")
    if lcr.inputs():
        lcr['width'].setValue(lcr.input(0).width())
        lcr['height'].setValue(lcr.input(0).height())
    else:
        lcr['width'].setValue(nuke.root().width())
        lcr['height'].setValue(nuke.root().height())

nuke.knobDefault("LayerContactSheet.showLayerNames","True")
nuke.toolbar("Nodes").addMenu("Merge", "ToolbarDraw.png").addCommand("LayerContactSheet",
    "create_layerContactSheet()", icon= "LayerContactSheet.png")


###########################
# Text: add frame number
def create_textNode():
    nuke.knobDefault("Text2.message", "[frame]")
    nuke.knobDefault("Text2.xjustify","centre")
    nuke.knobDefault("Text2.yjustify","centre")
    tt = nuke.createNode("Text2")
    tt['box'].setValue([0, 0, tt.width(), tt.height()])
nuke.toolbar("Nodes").addMenu("Draw", "ToolbarDraw.png").addCommand("Text",
    "create_textNode()", icon= "Text.png")

###########################
#Resurrect old text node
#has a missing font on centos... could we create a Text2 then copy the font?
nuke.toolbar("Nodes").addMenu("Draw", "ToolbarImage.png").addCommand("Text (old)",
    "nuke.createNode('Text')", icon= "Text.png")


###########################
# StickyNotes: add current user info
# and frame number
def create_StickyNote():
    import nuke, os, datetime
    try:
        import pwd
        if pwd.getpwuid(os.getuid())[4]:
            username = pwd.getpwuid(os.getuid())[4]
        else:
            username = pwd.getpwuid(os.getuid())[0]
    except:
        username= os.getenv("USERNAME")
    #print(username)
    today = datetime.datetime.now().strftime("%d %B %Y, %H:%M")
    result = '%s, %s\nframe: %d\n'%(username, today, nuke.frame())
    #create the note
    sticky = nuke.createNode("StickyNote")
    sticky.knob("label").setValue(result)
    sticky.knob("selected").setValue(False)
    return

nuke.toolbar("Nodes").addMenu("Other", "ToolbarOther.png").addCommand("StickyNote",
    "create_StickyNote()", "Alt+n", icon= "StickyNote.png", shortcutContext= dagContext)



#fix points to 3d:
def PointsTo3D_callback():
    #fixes points to 3d so it makes keyframes automatically
    #by Sean Danischevksy, 2017, but meaning to write it since the node came out 
    if nuke.thisKnob().name() == 'pointA':
        nuke.thisNode()['ref_timeA'].clearAnimated()#clear previous animation
        nuke.thisNode()['ref_timeA'].setAnimated()#ready knob for animation
        nuke.thisNode()['ref_timeA'].setValue(nuke.frame())#set keyframe (current frame) at current frame
    elif nuke.thisKnob().name() == 'pointB':
        nuke.thisNode()['ref_timeB'].clearAnimated()
        nuke.thisNode()['ref_timeB'].setAnimated()
        nuke.thisNode()['ref_timeB'].setValue(nuke.frame())
    elif nuke.thisKnob().name() == 'pointC':
        nuke.thisNode()['ref_timeC'].clearAnimated()
        nuke.thisNode()['ref_timeC'].setAnimated()
        nuke.thisNode()['ref_timeC'].setValue(nuke.frame())
    return

nuke.addKnobChanged(PointsTo3D_callback, nodeClass= 'PointsTo3D')

'''
#disk_cache shortcut - this can be annoying so I took it out
nuke.toolbar("Nodes").addMenu("Other", "ToolbarOther.png").addCommand("DiskCache", 
    "nuke.createNode('DiskCache')", ",", shortcutContext= dagContext, icon="DiskCache.png") 
'''
pass