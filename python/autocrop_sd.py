import nuke
import nukescripts

def _node_range(node):
    #this node's own first/last frame, falling back to the root range if the
    #node doesn't report one.
    try:
        return int(node.firstFrame()), int(node.lastFrame())
    except:
        return (int(nuke.root()['first_frame'].value()),
                int(nuke.root()['last_frame'].value()))

def autocrop(layer= 'rgba'):
    #put an auto-crop after EACH selected node, using that node's OWN input
    #first/last frame instead of the project (root) frame range.
    #
    #the stock nukescripts.autocrop() takes a single range and applies it to
    #every selected node, so a combined min->max range would scan out-of-range
    #frames for the shorter clips. run it once per node, each over its own
    #range, so nodes with different frame ranges each get cropped correctly.

    nodes= nuke.selectedNodes()
    if not nodes:
        nuke.message("Please select a node to auto-crop.")
        return []

    newcrops= []
    for node in nodes:
        first, last= _node_range(node)

        #select just this node and auto-crop it over its own range
        for n in nuke.selectedNodes():
            n['selected'].setValue(False)
        node['selected'].setValue(True)

        before= set(n.name() for n in nuke.allNodes())
        nukescripts.autocrop(first= first, last= last, inc= None, layer= layer)
        newcrops += [n for n in nuke.allNodes()
                     if n.name() not in before and 'box' in n.knobs()]

    #leave the new crops selected
    for n in nuke.allNodes():
        n['selected'].setValue(False)
    for c in newcrops:
        c['selected'].setValue(True)

    return newcrops
