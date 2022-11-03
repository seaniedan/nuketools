import nuke

def calculate_tidyness(nodes):
    #Calculate tidiness metric for nuke nodes based on 
    #the following bad behaviours:
    #uniquely positioned nodes
    #upward noodles
    #tangloed (crossed) noodles


    def getuniquePos(nodes):
        from collections import defaultdict
        #count uniquely positioned Nuke nodes
        #uniquePos= 0 #count of nodes which don't line up with any other nodes.
                     #i.e.  x position is unique AND y position is unique
        uniquePos= []# nodes which don't line up with any other nodes, i.e. x position is unique AND y position is unique
        xxyy= [(node, node['xpos'].getValue(), node['ypos'].getValue()) for node in nodes]
        node, xx, yy= list(zip(*xxyy))
        for node, x, y in xxyy:
            if xx.count(x) == 1 and yy.count(y) == 1:
                uniquePos.append(node)
        #print 'untidy nodes:'
        #print ", ".join(sorted([node.name() for node in uniquePos],key= str.lower))
        #print len(uniquePos)
        return uniquePos
    
    
    def getUpNoodles(nodes):
        from collections import defaultdict
        #count upward arrows
        up= []
        count= 0
    
        #deps= [(node['ypos'].getValue(), nuke.dependentNodes(nuke.INPUTS, node)) for node in nodes]
    
        for node in nodes:
            for dep in nuke.dependentNodes(nuke.INPUTS, node):
                if dep.Class() not in ignoreClasses:
                    #count+= 1
                    if dep['ypos'].getValue()< node['ypos'].getValue():
                        up.append(node)
        return up
    
    
    def getTangledNoodles(nodes):
        #count crossed wires un Nuke graph
    
        def ccw(A, B, C):
            #check for sign changes (using counter clockwise?)
            #from http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
            return (C.ypos()- A.ypos())* (B.xpos()- A.xpos()) > (B.ypos()- A.ypos())* (C.xpos()- A.xpos())
    
        def intersect(xxx_todo_changeme, xxx_todo_changeme1):
            #check whether lines A-B and C-D cross
            #print (A.xpos(), A.ypos()),(B.xpos(), B.ypos()),(C.xpos(), C.ypos()),(D.xpos(), D.ypos())
            #first check if they are the same, if so return false:
            (A, B) = xxx_todo_changeme
            (C, D) = xxx_todo_changeme1
            if (A.xpos(), A.ypos()) == (C.xpos(), C.ypos()) or (A.xpos(), A.ypos()) == (D.xpos(), D.ypos()) or (B.xpos(), B.ypos()) == (C.xpos(), C.ypos()) or (B.xpos(), B.ypos()) == (D.xpos(), D.ypos()) :
               return
            else:
            #print A,B,C,D
                if ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D):
                    return ((A, B), (C, D))
    
    
        #ignoreClasses= ['Viewer', 'BackdropNode']
        #nodes= [node for node in nodes if node.Class() not in ignoreClasses]
    
        #make pair of nodes for all lines
        lines = []
    
        for node in nodes:
            for dep in node.dependencies(nuke.INPUTS): #only visible pipes, not expressions
                if dep.Class() not in ignoreClasses and dep in nodes:
                    lines.append((node, dep))
                    #print node.name(), dep.name()
    
    
        #list combinations of noodles to check
        import itertools
        to_check= list(itertools.combinations(lines, 2))
    
        #for debugging
        #for lineA, lineB in to_check:
            #if intersect(lineA, lineB):
                #cross="X"
            #else:
                #cross="-"
            #print "(%s, %s)%s(%s,%s)"%(lineA[0].name(), lineA[1].name(), cross, lineB[0].name(), lineB[1].name())
    
    
        #return intersecting noodles
        intersections= [intersect(*i) for i in to_check]
        return [i for i in intersections if i]
    
    #store original nodes, do I can restore at end: otherwise, for example, 
    #nodes, uniquePos, up, tangled= seanscripts.tidyness_sd.calculate_tidyness(nodes)
    #will overwrite my original selection.
    original_nodes= nodes

    ignoreClasses= ['Viewer', 'BackdropNode']
    nodes= [node for node in nodes if node.Class() not in ignoreClasses]
    
    uniquePos= getuniquePos(nodes)

    up= getUpNoodles(nodes)

    tangled= getTangledNoodles(nodes)

    #restore original nodes
    nodes= original_nodes
    return (nodes, uniquePos, up, tangled)#, tidyness)



def show_tidyness(nodes):
    #run the tidyness metric, and display result.
    #nodes= nuke.selectedNodes() or nuke.allNodes()
    nodes, uniquePos, up, tangled= calculate_tidyness(nodes)

    #print the result
    print(('%d untidy nodes:' % len(uniquePos)))
    print((", ".join(sorted([node.name() for node in uniquePos], key= str.lower))))

    print(('\n%d upstreaming nodes:' % len(up)))
    print((", ".join(sorted([node.name() for node in up], key= str.lower))))

    print(('\n%d tangled noodles:' % len(tangled)))

    #for debugging
    #for lineA, lineB in to_check:
        #if intersect(lineA, lineB):
            #cross="X"
        #else:
            #cross="-"
        #print "(%s, %s)%s(%s,%s)"%(lineA[0].name(), lineA[1].name(), cross, lineB[0].name(), lineB[1].name())

    print(("\n".join(sorted(["(%s, %s)%s(%s, %s)"%(lineA[0].name(), lineA[1].name(), "x", lineB[0].name(), lineB[1].name()) for lineA, lineB in tangled], key= str.lower))))  

    #select the offending nodes
    [node.setSelected(0) for node in nuke.allNodes()]
    #[node.setSelected(1) for node in nodes if node in uniquePos or node in up or node in [[lineA[0], lineB[0]] for lineA, lineB in tangled]]
    [node.setSelected(1) for node in nodes if node in [(lineA[0], lineB[0]) for lineA, lineB in tangled]]
    a=[(lineA[0], lineB[0]) for lineA, lineB in tangled]
    #print 'a', a
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



    print(('\nunique position tidyness: %.2f'% uniquePostidyness))
    print(('\ndownward flow only tidyness: %.2f'% uptidyness))
    print(('\nuntangled noodle tidyness: %.2f'% untangletidyness))
    print(('\nout of %d nodes'% len(nodes)))
    #print nodes
    tidyness= ((uniquePostidyness* uniquePosweighting)+ (uptidyness* upweighting)+(untangletidyness* untangleweighting))* 10

    
    print(('\nTidyness: %.2f'% tidyness))
    #tidyness=len(uniquePos)/ float(len(nodes))
    #show the metric
    msg= "%d uniquely positioned nodes\n%d upward arrows\n\n%d tangled noodles\nout of %d nodes.\nTidyness = %.1f out of 10"% (len(uniquePos), len(up), len(tangled),len(nodes), tidyness)
    nuke.message(msg)

if __name__ == '__main__':
    show_tidyness(nuke.allNodes())



