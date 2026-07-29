import nuke

def _sample(box, f):
    #return the four box channel values (x, y, r, t) at frame f
    return (box.getValueAt(f, 0), box.getValueAt(f, 1),
            box.getValueAt(f, 2), box.getValueAt(f, 3))

def _covering_box(box):
    #smallest STATIC box that covers the (possibly animated) box over its
    #frame range, ignoring blank (0,0,0,0) frames which auto-crop emits for
    #empty images. returns None if every sampled frame is blank.
    if box.isAnimated():
        times= [k.x for i in range(4) if box.animation(i)
                for k in box.animation(i).keys()]
        first, last= int(min(times)), int(max(times))
    else:
        first= last= int(nuke.frame())

    xmin= ymin= rmax= tmax= None
    for f in range(first, last+ 1):
        x, y, r, t= _sample(box, f)
        if x== 0 and y== 0 and r== 0 and t== 0:
            continue
        if xmin is None:
            xmin, ymin, rmax, tmax= x, y, r, t
        else:
            xmin= min(xmin, x)
            ymin= min(ymin, y)
            rmax= max(rmax, r)
            tmax= max(tmax, t)

    if xmin is None:
        return None
    return (xmin, ymin, rmax, tmax)

def static_bbox(nodes= None):
    #for each selected node that has a 'box' knob (e.g. an auto-crop Crop),
    #create a STATIC Crop whose box is the union of the source box over its
    #frame range: the smallest fixed box that fully covers the animated one.
    #if nothing with a box is selected, offer to auto-crop the selection first.

    if nodes is None:
        nodes= nuke.selectedNodes()

    #use any selected nodes that already have a box (e.g. Crops); ignore the rest
    box_nodes= [n for n in nodes if 'box' in n.knobs()]

    via_autocrop= False
    autocrop_layer= None

    #nothing to collapse: offer to auto-crop first. auto-crop needs a node to
    #attach to, so this is only possible when something is actually selected.
    if not box_nodes:
        if not nodes:
            nuke.message("Please select a node: a Crop to collapse, "
                         "or any node to auto-crop first.")
            return []

        #the layer chooser doubles as the confirm dialog; Cancel aborts
        p= nuke.Panel("Auto-crop before static bbox")
        p.addEnumerationPulldown("auto-crop layer", "rgba alpha rgb")
        if not p.show():
            return []
        autocrop_layer= p.value("auto-crop layer")

        import autocrop_sd
        before= set(n.name() for n in nuke.allNodes())
        autocrop_sd.autocrop(layer= autocrop_layer)
        box_nodes= [n for n in nuke.allNodes()
                    if n.name() not in before and 'box' in n.knobs()]
        if not box_nodes:
            return []
        via_autocrop= True

    newnodes= []
    for node in box_nodes:
        cover= _covering_box(node['box'])

        if cover is None:
            #every frame was blank
            if via_autocrop:
                nuke.message("Auto-crop on '%s' found no non-zero pixels on "
                             "any frame. Try a different layer (e.g. alpha)."
                             % autocrop_layer)
                continue          #don't leave a useless 0,0,0,0 static crop
            cover= (0, 0, 0, 0)   #manually-selected blank crop: keep as-is

        xmin, ymin, rmax, tmax= cover

        #make the new static Crop
        newnode= nuke.nodes.Crop()
        newnode.setXYpos(node.xpos(), node.ypos()+ node.screenHeight())
        newnode.setInput(0, node)
        newnode['box'].setValue((xmin, ymin, rmax, tmax))
        newnode['crop'].setValue(True)

        #name it, de-duplicating with a numeric suffix if needed
        newNameFormat= "%s_staticbbox" % node.name()
        if nuke.exists(newNameFormat):
            i= 1
            newNameFormat= "%s_staticbbox%d" % (node.name(), i)
            while nuke.exists(newNameFormat):
                i+= 1
                newNameFormat= "%s_staticbbox%d" % (node.name(), i)
        newnode.setName(newNameFormat)
        newnodes.append(newnode)

    return newnodes
