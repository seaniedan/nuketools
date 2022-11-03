#!/usr/bin/env python3

import nuke

def select_left_to_right(nodes= nuke.selectedNodes()):
    #################################################
    # select_left_to_right by Sean Daniscehevsky 2022
    # sorts select order of nodes from left to right 
    # on the node graph,
    # ready for a contact sheet or append clip node

    nodes.sort(key= lambda node: node.xpos())
    [node.setSelected(0) for node in nodes]
    [node.setSelected(1) for node in nodes]
    return nodes


if __name__=="__main__":
    select_left_to_right()
