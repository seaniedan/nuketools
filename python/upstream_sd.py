#this is the best one:
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



#this one worked but I improved it
def upstream(startNode= None, nodes= None, what= nuke.EXPRESSIONS|nuke.INPUTS|nuke.HIDDEN_INPUTS, enter_groups= False ):
    #return upstream nodes, recursive. Enter groups if required.
    try:
        if nodes is None:
            #first time round the loop based on this startNode
            nodes= [] #{} dict of whether we have recursed each node
        node = startNode
        if not node:
            return
        else:
            print(('node:', node.name()))
            print(('nodes:', [i.name() for i in nodes]))
            upNodes= nuke.dependencies(node, what)
            for n in upNodes:
                if n not in nodes:
                    #add to set
                    nodes.append(n)
                    if enter_groups:
                        if n.Class() == "Group":
                            group= nuke.toNode(n.name())
                            with group:
                                outputs= nuke.allNodes('Output')
                                for o in outputs:
                                    upstream(o, nodes= nodes, what= what)
                    upstream(n, nodes= nodes, what= what)
    except RuntimeError:
        #print "Maximum recursion reached?
        return list(nodes)
    return list(nodes)


'''
import time
t0 = time.time()
#code block
nodeList = upstream(nuke.selectedNode())
print nodeList
'''
t1 = time.time()
total = t1-t0
print((nuke.selectedNode().name()+": "+ str(total)+' seconds.'))

#Blur2: 0.0187239646912 seconds.
#Blur 2: 113.141684055 seconds
#

'''
test script:


set cut_paste_input [stack 0]
version 10.0 v6
push $cut_paste_input
Blur {
 size {{parent.Blur5.size}}
 name Blur6
 selected true
 xpos 458
 ypos -496
}
Blur {
 inputs 0
 size {{parent.Blur6.size}}
 name Blur5
 selected true
 xpos 581
 ypos -413
}
Blur {
 size {{parent.Blur4.size}}
 name Blur3
 selected true
 xpos 387
 ypos -139
}
Blur {
 inputs 0
 size {{parent.Blur3.size}}
 name Blur4
 selected true
 xpos 264
 ypos -222
}
Blur {
 size {{parent.Blur1.size}}
 name Blur2
 selected true
 xpos 205
 ypos 10
}
Blur {
 inputs 0
 size {{parent.Blur2.size}}
 name Blur1
 selected true
 xpos 82
 ypos -73
}
'''

#this next one works but it doesn't have all the options
def get_dependent_nodes(nodes):
    """
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

#print get_dependent_nodes(nuke.selectedNodes())


def select_upstream(nodes, what= nuke.EXPRESSIONS|nuke.INPUTS|nuke.HIDDEN_INPUTS, backdrops= True, select= True):
#was going to add
#, dependent_file_generators= True):

#select all upstream nodes (dependencies) of given nodes
#and optionally backdrops if the nodes are on backdrops
#by Sean Danischevsky 2014

#inputs: nodes= initial nodes to start recuring from
#You can use the following constants or'ed together to select the types of dependencies that are looked for:
#nuke.EXPRESSIONS = expressions
#nuke.INPUTS = visible input pipes
#nuke.HIDDEN_INPUTS = hidden input pipes.
#The default is to look for all types of connections.

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

    #recursive search
    upstreamNodes= nuke.dependencies(nodes, what) 
    c=1
    while (len(set(upstreamNodes)) > len(set(nodes))) and c < 10:
        c+= 1 
        nodes+= upstreamNodes 
        nodes= list(set(nodes))
        upstreamNodes= nuke.dependencies(upstreamNodes, what)
        print(nodes) 
    print(c)
    if backdrops:
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
    return list(set(nodes))

nodes=nuke.selectedNodes()
select_upstream(nodes, what= nuke.EXPRESSIONS|nuke.INPUTS|nuke.HIDDEN_INPUTS, backdrops= True, select= True)


