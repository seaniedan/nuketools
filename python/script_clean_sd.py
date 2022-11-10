import nuke

#testing= False
#testing = True

#TO DO
##don't delete dots if they have expression dependents (had a node with expressions in the dots)
#delete dots if the only output is a viewer
#add 'clear all checkboxes' function, or only add checkbox if function is needed
#clean script should then also run tidy, and keep going until all fixed.

##delete disabled nodes###
##includes improved delete function

def node_delete2(sel, popupOnError= True):
    #replaces nukescripts.node_delete with Sean Danischevsky's fixed version
    sel= set(sel)
    unsel= set(nuke.allNodes())- sel- set(nuke.allNodes("Viewer"))    
    hidden_inputs= set(nuke.dependencies(list(unsel), nuke.HIDDEN_INPUTS))
    hidden_inputs_list= hidden_inputs.intersection(sel)
    expres_links= set(nuke.dependencies(list(unsel), nuke.EXPRESSIONS))
    expres_links_list= expres_links.intersection(sel)

    if hidden_inputs_list or expres_links_list:
        if popupOnError:
            msg= "Warning:\n"
            if hidden_inputs_list: 
                msg+= "hidden inputs are connected to\n%s"% (', '.join([i.fullName() for i in hidden_inputs_list]))

            if hidden_inputs_list and expres_links_list: 
                msg+= "\nand "
            if expres_links_list: 
                msg+= "expressions are linked to\n%s"% (', '.join([i.fullName() for i in expres_links_list]))
            msg+= "\nDelete anyway?"
            if not nuke.ask(msg):
                #user cancels or says no
                return
        else:
            sel= sel- hidden_inputs_list- expres_links_list
    for i in sel:
        nuke.delete(i)
    return

def file_dependencies(startNode):
    #by Sean Danischevsky 2018
    #Looks for file generators who may have made a file in your nuke script. 
    #input: a nuke node
    #returns: a list of nodes which may have made that input
    reader_writer_dict= {'Read': {'Write':('file','proxy'), 'WriteTank': ('cached_path', 'tk_cached_proxy_path')}}
    possible_writer= reader_writer_dict[startNode.Class()]
    for possible_write, knobs in list(possible_writer.items()):
        possible_nodes= nuke.allNodes(possible_write)
        print(possible_nodes)
    dependent_file_generators= possible_writer
    return dependent_file_generators


def upstream(startNode, nodes= None, what= nuke.EXPRESSIONS|nuke.INPUTS|nuke.HIDDEN_INPUTS, enter_groups= False, add_file_creators= False ):
    #by Sean Danischevsky 2018
    #return upstream Nuke nodes, recursively. 


    #startNode can be a node or list of nodes.
    #You can use the following constants or'ed together to select the types of dependencies that are looked for:
    #nuke.EXPRESSIONS = expressions
    #nuke.INPUTS = visible input pipes
    #nuke.HIDDEN_INPUTS = hidden input pipes.
    #The default is to look for all types of connections.
    #enter_groups= Enter groups if required.
    #add_file_creators= attempt to include creators of files, e.g. Write nodes that may have made an output used in selected Read nodes.


    #these lines are required for recursive evaluation
    if nodes == None: 
        nodes= []

    #start loop
    if startNode:
        searchDependencies= nuke.dependencies(startNode)
        if add_file_creators:
            searchDependencies+= file_dependencies(startNode, what)

        for node in nuke.dependencies(startNode, what):
            if node not in nodes:
                print('(added)')
                #add to list
                nodes.append(node)
                if enter_groups and node.Class() == "Group":
                    #enter the group and add contents also
                    group= nuke.toNode(node.name())
                    with group:
                        outputs= nuke.allNodes('Output')
                        for output in outputs:
                            upstream(output, nodes= nodes, what= what)
                #go upstream of the node
                upstream(node, nodes= nodes, what= what)
        return list(nodes)
    else:
        return


def select_upstream_sd(nodes, backdrops= True, select= True, add_file_creators= False):#, dependent_file_generators= True):
    #by Sean Danischevsky 2014
    #select all upstream nodes (dependencies) of given nodes
    #and optionally backdrops if the nodes are on backdrops
    #TO DO: 
    #dependent file generators = test for whether the Reads are dependent on Writes in the script
    #i.e. precomps
    #would be good to test for vectorfields etc and other file generators and readers.

    #inputs: nodes= initial nodes to start recuring from
    #You can use the following constants or'ed together to select the types of dependencies that are looked for:
    #nuke.EXPRESSIONS = expressions
    #nuke.INPUTS = visible input pipes
    #nuke.HIDDEN_INPUTS = hidden input pipes.
    #The default is to look for all types of connections.
    if nodes:

        def bdNodes(bdNode):
            #return list of nodes on a given BackdropNode
            origSel= nuke.selectedNodes() # STORE CURRENT SELECTION
            [n.setSelected(False) for n in origSel]
            bdNode.selectNodes()  # SELECT NODES IN BACKDROP
            bdNodes = nuke.selectedNodes() # STORE NODES
            # RESTORE PREVIOUS SELECTION:
            bdNode.selectNodes( False )
            [n.setSelected(True) for n in origSel]
            return bdNodes

        bds= [] #list of backdrop nodes containing selected or dependent nodes

        #recursive dependencies (upstream nodes)
        nodes+= upstream(nodes)

        #add backdrops
        if backdrops:
            #add backdrops:
            for bd in nuke.allNodes("BackdropNode"):
                allNodesOnBD= bdNodes(bd)
                for node in nodes:
                    if node in allNodesOnBD:
                        nodes.append(bd)

        #remove any duplicates
        nodes= list(set(nodes))

        #select them
        if select:
            [node.setSelected(True) for node in nodes]
        #return the list
        return list(set(nodes))

def select_downstream(nodes, backdrops= True, select= True):
#select all nodes downstream (dependents) of given nodes, 
#and optionally backdrops if the nodes are on backdrops
#by Sean Danischevsky 2014
 
    #flatten lists
    flatten= lambda l: sum(list(map(flatten, l)), []) if isinstance(l, list) else [l]

    def bdNodes(bdNode):
        #return list of nodes on a given BackdropNode
        origSel= nuke.selectedNodes() # STORE CURRENT SELECTION
        [n.setSelected(False) for n in origSel] #deselect original nodes
        bdNode.selectNodes()  # SELECT NODES IN BACKDROP
        bdNodes= nuke.selectedNodes() # STORE NODES
        #RESTORE PREVIOUS SELECTION:
        bdNode.selectNodes(False)
        [n.setSelected(True) for n in origSel]
        return bdNodes

    downstreamNodes= list(set(flatten([i.dependent() for i in nodes])))

    while downstreamNodes: 
        nodes+= downstreamNodes 
        downstreamNodes= list( set( flatten( [i.dependent() for i in downstreamNodes])))
        nodes= list(set(nodes))

    if backdrops:
        #keep list of backdrop nodes containing selected or dependent nodes
        bds= []
        #add backdrops:
        for bd in nuke.allNodes("BackdropNode"):
            allNodesOnBD= bdNodes(bd)
            for node in nodes:
                if node in allNodesOnBD:
                    nodes.append(bd)
    nodes= list(set(nodes))
    if select:
        [node.setSelected(True) for node in nodes]
    #return the list
    return nodes


##########################
##########################


def delete_all_errored_nodes(nodes):
    #delete all errored nodes
    [nuke.delete(node) for node in nodes if node.error()]

def set_cards_to_one_row_one_column(nodes):
    #set cards to have only one row, one column
    nodes= [node for node in nodes if node.Class() == 'Card2']
    no_distort={'lens_in_distort_a':0.0, 'lens_in_distort_b':0.0, 'lens_in_distort_c':0.0, 'lens_in_distortion':0.0, 'type':'none'}
    [[node['rows'].setValue(1), node['columns'].setValue(1) ] for node in nodes if [node[k].value() == v for k, v in list(no_distort.items())]]

def clear_transform_expressions(nodes):
    #clears the python exec from linked trackers. Should really test for the exact code.
    nodes= [node for node in nodes if node.Class() == 'Transform']
    for node in nodes:
        try:
            if node['invert'].hasExpression():
                node['invert'].clearAnimated()
        except:
            pass

def unhide_inputs(nodes):
    #unhide inputs
    for node in nodes:
        if node.Class() not in ['Viewer'] and 'hide_input' in  node.knobs():
            node['hide_input'].setValue(False)

def merge_bbox_set(nodes):
    #set merges to my usual defaults... 
    #can cause problems in certain circumstances...! 
    #If so, go through the changed nodes and check
    #especially anything changed to 'intersection'.
    #only adjusting bbox 'inwards'
    prefs_merge2_bbox= {'multiply': 'intersection', 
                        'stencil': 'B',
                        'mask': 'intersection', 
                        'in': 'intersection'}
    # 'max' must stay as union - adding rotoshapes for example
    # better to change 'in' to something else
    nodes = [node for node in nodes if node.Class() in ('Merge', 'Merge2')]
    for node in nodes:
        #check if there's a mask input... that could get messy...
        if node.inputs()> 2 and node.input(2) != None:
            #so just warn and don't change in that case
            print(("Check %s node %s: it has a mask input. Messy!" % (node.Class(), node.name())))
        else:
            #is the merge operation in the prefs_merge2_bbox dictionary?
            if node['operation'].value() in list(prefs_merge2_bbox.keys()):
                #is it not the preferred case?
                if node['bbox'].value()!= prefs_merge2_bbox[node['operation'].value()]:
                    #if bbox isn't union, the user has thought about it, so warn but don't change
                    if node['bbox'].value()!= 'union':
                        print(("Check %s node %s (%s): should bbox change from %s to %s?" % (node.Class(), node.name(),node['operation'].value(), node['bbox'].value(), prefs_merge2_bbox[node['operation'].value()])))
                    else:
                        #else change the value 
                        print(("Changing %s node %s (%s) bbox from %s to %s" % (node.Class(), node.name(), node['operation'].value(), node['bbox'].value(), prefs_merge2_bbox[node['operation'].value()])))
                        node['bbox'].setValue(prefs_merge2_bbox[node['operation'].value()])

def delete_dots(nodes):
    #remove additional dots
    #keep any with labels
    del_list= []
    for node in nodes:
        if node.Class()== 'Dot' and not node['label'].value():
            del_list.append(node)

    #return new list - must create new list before deleting nodes!
    if del_list:
        nodes= list(set(nodes)- set(del_list))
        node_delete2(sel= del_list, popupOnError= True)
    return nodes


def delete_disabled_nodes(nodes):
    #delete disabled nodes
    del_list= []
    for node in nodes:
        if 'disable' in node.knobs():
            if node['disable'].toScript() == 'true': #yes, toScript returns lower case
                #only delete if node is disabled manually, not due to expressions etc 
                print(('Will try to delete disabled node %s' % node.name())) 
                del_list.append(node)

    #return new list - must create new list before deleting nodes!
    if del_list:
        nodes= list(set(nodes)- set(del_list))
        node_delete2(sel= del_list, popupOnError= True)
    return nodes



def make_dots(nodes):
    #create dots under nodes with multiple outputs
    for node in nodes:
        if (node.Class() not in ['Dot', 'Viewer']):
            #get visible outputs, ignore invisible nodes FnNukeMultiTypeOpIop1, FnNukeMultiTypeOpIop nodes created by TimeOffset 
            #maybe this couldbe done by comparing nuke.allNodes to the dependent nodes. But what about nodes in groups etc. So for now:
            outputs= [o for o in nuke.dependentNodes(nuke.INPUTS, node) if not o.Class().startswith('FnNukeMultiTypeOpIop')]
            if len(outputs)> 1:
                print(('Adding a dot under %s, as it has multiple outputs (%s)' % (node.fullName(),', '.join([o.fullName() for o in outputs]))))
                n= nuke.nodes.Dot()
                n.setInput(0, node)
                nuke.autoplaceSnap(n)
                for i in outputs:
                    for j in range(i.inputs()):
                        if i.input(j) == node:
                            #print 'setting %s input %d to the dot under %s' % (i.name(),j, node.fullName())
                            i.setInput(j, n)

#make_dots(nuke.selectedNodes())

def turn_off_keyframes_tracker4s(nodes):
    #turn off keyframes on Tracker4's as they take forever and are unncecessary
    for node in nodes:
        if node.Class() == "Tracker4":
            if node['keyframe_display'].setValue(3):
                print(('Turned off keyframe display in %s'% (node.name())))
    return

#turn_off_keyframes_tracker4s(nuke.selectedNodes())


def replace_transformMasked(nodes):
    #create new Transform node under each TransformMasked, delete original TransformMasked
    del_list= [] #hold the TrasformMasked to delete
    for node in nodes:
        if node.Class() == "TransformMasked":
            if not node.input(1):
                #it doesn't have 'mask' input
                if node['channels'].value() == 'all' and node['mix'].value() == node['mix'].defaultValue() and not nuke.dependentNodes(nuke.EXPRESSIONS, node):
                    #it doesn 't have 'mix' etc in..
                    #annoyingly node['channels'] doesn't have a defaultValue()
                    #create Transform underneath
                    [n.setSelected(0) for n in nuke.allNodes()]
                    node.setSelected(1)
                    newNode= nuke.createNode('Transform', 
                            node.writeKnobs(nuke.WRITE_USER_KNOB_DEFS | nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_SCRIPT), 
                            inpanel= False)
                    del_list.append(node)

    #delete the replaced nodes
    #return new list - must create new list before deleting nodes!
    if del_list:
        nodes= list(set(nodes)- set(del_list))
        node_delete2(sel= del_list, popupOnError= True)
    return nodes

def place_viewers_at_top_left(nodes):
    #place viewer nodes at top left of Nuke's DAG
    viewers= [node for node in nodes if node.Class() in ['Viewer']]
    #viewers= nuke.allNodes('Viewer')
    otherNodes= list(set(nodes) -set(viewers))
    minxy= (min(node.xpos() for node in otherNodes), min(node.ypos() for node in otherNodes))
    for i, viewer in enumerate(viewers):
        #lay out viewers in a horizontal line just above the top leftmost node
        viewer.setXYpos(minxy[0]+ (i* viewer.screenWidth()), minxy[1]+ 50)
        nuke.autoplace(viewer)



def hide_viewer_inputs(nodes):
    #hide viewer inputs
    [node['hide_input'].setValue(True) for node in nodes if node.Class() in ['Viewer']      ]



def hide_viewer_inputs(nodes):
    #set localization value to 'from auto-localize path'
    #this probably better achieved by Cache -> Force Update -> All
    for node in nodes:
        try:
            node['localizationPolicy'].setValue(1)
        except:
            pass    






def tidy(nodes):
    #tidy nodes and backdrops.
    #to do: align b lines etc.

    import tidyness_sd

    if not nodes:
        nodes= nuke.allNodes()
    
    #set up a panel to show options and current tidyness level

    #show tidyness
    nodes, uniquePos, up, tangled= tidyness_sd.calculate_tidyness(nodes)
    #set weightings
    uniquePosweighting= .333
    upweighting= .333
    untangleweighting= .333

    try:
        uniquePostidyness= 1-(len(uniquePos)/ float(len(nodes)))
    except ZeroDivisionError:
        uniquePostidyness= 1

    try:
        uptidyness= 1- (len(up)/ float(len(nodes)))
    except ZeroDivisionError:
        uptidyness= 1

    try:
        untangletidyness= 1- (len(tangled)/ float(len(nodes)))
    except ZeroDivisionError:
        untangletidyness= 1

    tidyness= ((uniquePostidyness* uniquePosweighting)+ (uptidyness* upweighting)+(untangletidyness* untangleweighting))* 10
    msg= "Cleanup script: tidyness = %.1f out of 10"% (tidyness)
    #panel.addSingleLineInput('Range:', rangeDisplay)

    #remember, as a dict, these don't happen in order:
    tidy_options= { delete_disabled_nodes: 'delete disabled nodes',
                    unhide_inputs: 'unhide inputs',
                    merge_bbox_set: 'set Merge bounding boxes',
                    make_dots: 'make dots under nodes with multiple outputs',
                    delete_dots: 'delete unnecessary dots',
                    turn_off_keyframes_tracker4s: 'turn off Tracker keyframe generation (speeds up script)',
                    clear_transform_expressions: 'clear Transform expressions (speeds up script)',
                    set_cards_to_one_row_one_column: 'set Cards to one row one column (reduce unnecessary vertices)',
                    replace_transformMasked: 'replace TransformMasked nodes with regular Transforms where possible',
                    place_viewers_at_top_left: 'place viewer nodes at top left of DAG',
                    hide_viewer_inputs: 'hide viewer inputs'
                    }

    #Ask the user
    panel= nuke.Panel(msg)
    #panel.setWidth(220)

    for check_name in sorted(tidy_options.values()):
        panel.addBooleanCheckBox(check_name, True)

    if panel.show(): 
        #display panel. Input from user.
        for check, check_name in list(tidy_options.items()):
            #print check.func_name
            #print len(nodes)
            #print ",".join([node.name() for node in nodes if node.Class() == 'Viewer'])
            if panel.value(check_name) == True:
                if check.__name__.startswith('delete') or check.__name__.startswith('replace'):
                    #reassign nodes for anything which deletes from selection
                    nodes= check(nodes) 
                else:
                    check(nodes)
    '''#delete_disabled_nodes(nodes)
    nukescripts.clear_selection_recursive()

    unhide_inputs(nodes)
    merge_bbox_set(nodes)
    #nodes= del_dots(nodes)  #just removed to see if it was causing problems
    make_dots(nodes)
    #turn off tracker keyframes: would be nice to actually export these
    turn_off_keyframes_tracker4s(nodes) 
    #clear expressions from transforms linked to trackers (the python callback really slows nuke):
    clear_transform_expressions(nodes)
    #set cards to 1x1 (unless they have distortion)
    set_cards_to_one_row_one_column(nodes)'''
    tidyness_sd.show_tidyness(nodes)


def cleanupScript(nodes):
    #clean up script 
    #by Sean Danischevsky 2016
    #if nodes selected:
    #select all upstream nodes 
    #else:
    #select all write nodes and
    #delete everything else
    #(except backdrops, viewers).
    #requires backdrop node tools etc.
    #
    import nukescripts

    nodes= select_upstream_sd(nodes, backdrops= True)

    #delete everything else, except viewers:
    delete_list= [node for node in nuke.allNodes() if (not node['selected'].value()) and node.Class() != "Viewer"]
    nodes_delete_list= list(set(delete_list).intersection(set(nodes)))
    if nodes_delete_list:
        nodes.remove(*nodes_delete_list)
    [nuke.delete(node) for node in delete_list]
    #print 44444,nodes
    #restore selection
    nukescripts.clear_selection_recursive()
    [node.setSelected(True) for node in nodes]

    #if viewers are the only nodes left unselected, select those too
    #before we run tidy nodes:
    #print "".join(set(node.Class() for node in nuke.allNodes() if not node['selected'].value())) == 'Viewer'
    if "".join(set(node.Class() for node in nuke.allNodes() if not node['selected'].value())) == 'Viewer':
        #viewers are the only nodes left unselected: select those too
        nodes= nuke.allNodes() 
        #print 11111
        #print ",".join([node.name() for node in nodes if node.Class() == 'Viewer'])
    #viewers= [node for node in nuke.allNodes() if node.Class() in ['Viewer']]
    #viewers= nuke.allNodes('Viewer')
    tidy(nodes)
    
    '''
    for node in original_sel:
        try:
            #print node.name()
            node.setSelected(True)
        except ValueError:
            print '!'
            pass
    '''





