import nuke
import nukescripts

def autocrop(layer= 'rgba'):
    #put an auto-crop after each selected node, using that node's OWN input
    #first/last frame instead of the project (root) frame range.
    #nukescripts.autocrop() falls back to root.first_frame/last_frame when
    #passed first=None/last=None, which is often wider than the actual footage.

    nodes= nuke.selectedNodes()
    if not nodes:
        nuke.message("Please select a node to auto-crop.")
        return

    #gather the frame range from the selected node(s)
    firsts= []
    lasts= []
    for node in nodes:
        try:
            firsts.append(int(node.firstFrame()))
            lasts.append(int(node.lastFrame()))
        except:
            #fall back to root range for this node if it has no reported range
            firsts.append(int(nuke.root()['first_frame'].value()))
            lasts.append(int(nuke.root()['last_frame'].value()))

    first= min(firsts)
    last= max(lasts)

    #hand off to the stock autocrop with an explicit range
    nukescripts.autocrop(first= first, last= last, inc= None, layer= layer)
