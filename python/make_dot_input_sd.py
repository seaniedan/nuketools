import nuke

def make_dot_input(nodes):
    #dot input script
    #creates a dot, and connects selected nodes to it.
    #by Sean Danischevsky 2013
    if nodes:
        dot = nuke.nodes.Dot(
            xpos= sum([node['xpos'].value() for node in nodes])/float(len(nodes)),
            ypos= min([node['ypos'].value() for node in nodes])- nuke.toNode("preferences")["GridHeight"].value()*6)
        nuke.autoplace(dot)
        for node in nodes:
            if dot.canSetInput(0, node):
                node.setInput(0, dot)
    else:
        nuke.message("Select some nodes!")
    return

###########################
#runs when testing:
if __name__ == "__main__":
    make_dot_input(nodes= nuke.selectedNodes())