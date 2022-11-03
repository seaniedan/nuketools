def paste_multiple():
    import nuke
    import nukescripts
    #alt+v to paste the same thing under all selected nodes
    #if no nodes selected, ask how many you want,
    #and whether to connect them to each other
    #by Sean Danischevsky 2014
    nodes= nuke.selectedNodes()

    if len(nodes) > 1:
        #paste to multiple node trees
        #deselect all nodes
        for sel in nodes:
            sel['selected'].setValue(False)
        #paste
        old_nodes= nuke.allNodes()
        for sel in nodes:
            sel['selected'].setValue(True)
            nuke.nodePaste(nukescripts.cut_paste_file())
            new_nodes= list(set(nuke.allNodes()) - set(old_nodes))
            [sel['selected'].setValue(True) for sel in new_nodes]
        return new_nodes
    else:
        #Paste to single or no node tree
        #Ask how many
        myPanel= nuke.Panel("Paste Multiple") 
        myPanel.addSingleLineInput("How many copies?", "") 
        myPanel.addBooleanCheckBox("Connect to each other", True if len(nodes)== 1 else True)
        copies= None
        if myPanel.show():
            copies= myPanel.value("How many copies?")
            try:
                copies= int(copies)
            except:
                    #user probably just wants one copy, so do that
                    copies= 1



            #make the copies
            old_nodes= nuke.allNodes()
            #print 'old', old_nodes
            connect= myPanel.value("Connect to each other")
            #print copies, connect
            for a_copy in range(copies):
                #paste copy
                nuke.nodePaste(nukescripts.cut_paste_file())
                if not connect:
                    nodes= nuke.selectedNodes()
                    nodes[-1].setInput(0, None)
            new_nodes= list(set(nuke.allNodes()) - set(old_nodes))
            #print 'nn', new_nodes
            [sel['selected'].setValue(True) for sel in new_nodes]
            #print new_nodes
            return new_nodes
        else:
            return


#runs when testing:
if __name__ == "__main__":
    paste_multiple()
