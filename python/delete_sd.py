###################   DELETE_sd
#by Sean Danischevsky 2010
#fix unnecessary warnings when deleting nodes
#the proper way to do this is to
#delete all the things we can, 
#then format a list to ask about the others.
#create and add to a list


import nuke, nukescripts

def node_delete(popupOnError=True):
  #replaces nukescripts.node_delete with Sean Danischevsky's fixed version
  #d = nuke.dependentNodes( nuke.EXPRESSIONS, nuke.selectedNodes() )
  sel= nuke.selectedNodes()
  #print 'sel=',sel
  unsel= list(    set(   nuke.allNodes()) - set(sel)   -set(nuke.allNodes("Viewer"))    )
  #print 'unsel=',unsel
  #if len(sel)>len(unsel):
    #print 'sel>unsel'
  hid = nuke.dependencies(unsel, nuke.HIDDEN_INPUTS)
  expres = nuke.dependencies(unsel, nuke.EXPRESSIONS)
  #print 'expres=',expres
  l= ""
  for i in hid:
    if i in sel:
      l= l+ i.fullName() + ", "
  exlist= ''
  for i in expres:
    if i in sel:
      exlist= exlist+ i.fullName()+ ", "
  if l or exlist:
     msg= "Warning:\n"
     if l: msg+= "hidden inputs are connected to\n%s"% l[:-2]
     if l and exlist: msg += "\nand "
     if exlist: msg+= "expressions are linked to\n%s"% exlist[:-2]
     msg+= "\nAre you sure you want to delete?"
     if not nuke.ask(msg):
         return
  nuke.nodeDelete()
  return
  
#replace builtin Nukescripts with version above:  
nukescripts.node_delete= node_delete