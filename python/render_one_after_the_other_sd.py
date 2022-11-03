import nuke

def renderSelected(nodes):
    # renders all selected (usually Write) nodes one by one, sorted by render order and using first/last frame of the write node to determine the range to render.
    # with thanks to Morten_Andersen
    # https://community.foundry.com/discuss/topic/124118/execute-write-node-after-other-write-finishes

    # disable proxy
    proxy = nuke.root()['proxy'].value()
    nuke.root()['proxy'].setValue(False)

    if all([i.Class() == 'Write' for i in nodes]):
        print ('All Write nodes')
        # sort by render order
        nodes.sort(key=lambda x: x['render_order'].value())

        # render!
        c = len(nodes)
        for i, node in enumerate(nodes, 1):
            if node['use_limit'].value():
                f = int(node['first'].value())
                l = int(node['last'].value())
            else:
                f= node.firstFrame()
                l= node.lastFrame()
            # execute node
            nuke.execute(node, f, l, 1)
            print(("%s node %d of %d, %s is done" % (node.Class(), i, c, node.name())))

    else:
        #not all Write nodes:
        # render!
        c = len(nodes)
        for i, node in enumerate(nodes, 1):
            f= node.firstFrame()
            l= node.lastFrame()
            print (node, f, l, 1)
            # execute node
            nuke.execute(node, f, l, 1)
            print(("%s node %d of %d, %s is done" % (node.Class(), i, c, node.name())))



    # set proxy back to original value
    nuke.root()['proxy'].setValue(proxy)


if __name__ == "__main__":
    #runs when testing:
    renderSelected(nuke.selectedNodes())

