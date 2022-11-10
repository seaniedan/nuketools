######################################
# MULTIPLE NODE INFO

import nuke, nukescripts

def multiple_node_info():
    ################################
    # information for multiple nodes
    # by Sean Danischevsky, 2012, 
    # 2015, 2022
    ################################

    def occurDict(items):
        #return number of times an item appears in a dictionary
        d = {}
        for i in items:
            if i in d:
                d[i] += 1
            else:
                d[i] = 1
        return d

    #get selected nodes or all nodes
    nodes= nuke.selectedNodes()

    #if 1 node, run updated
    #nukescripts.infoviewer()
    #/data/apps/cent5_x86_64/Nuke/6.3.6/nuke/plugins/nukescripts/info.py
    if len(nodes) == 1:
        if __name__ == "__main__":
            #runs when testing:
            nuke.display("get_all_node_info()", nodes[0])
        else:
            nuke.display("multiple_node_info_sd.get_all_node_info()", nodes[0])

    else:
        if not nodes:
            nodes= nuke.allNodes()
        
        #show how many nodes of different classes etc.
        #else run info on selected nodes
        #set up GUI: 
        #sort by name, class, no. of class?
        #count invisible inputs/disabled nodes?
        #errored nodes
        #info on biggest memory hogs
        #allow selection of a certain type, e.g. all disabled nodes
        #a= node['Class'].value()
        #a = (node['Class'].value() for node in nodes)
        d= occurDict(node.Class() for node in nodes)
        ranks= sorted(list(d.items()), key= lambda x: x[1], reverse= True)
        msg= "%s nodes:"% len(nodes)
        msg+= "\n=========================\n"
        #list the nodes
        for classes, rank in ranks:
            msg+= "%s: %s\n"%(classes, rank)
            msg+= "\n"
        msg+= f"\n{total_frames(nodes)} total frames."
        p= nuke.Panel('Multiple Node Info')
        p.addNotepad('nodes', msg)
        ret= p.show()
        return

    
def total_frames(nodes):
    return sum([node.lastFrame()- node.firstFrame()+ 1 for node in nodes])


def sizeof_fmt(num):
    for x in [' bytes','KB','MB','GB','TB']:
        if num< 1024.0:
            return "%3.2f%s" % (num, x)
        num /= 1024.0

def runProcess(exe):   
    import subprocess 
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
    while(True):
        retcode = p.poll() #returns None while subprocess is running
        line = p.stdout.readline()
        yield line
        if(retcode is not None):
            break


def get_all_node_info():
    #updated version of nuke node info by Sean Danischevsky 2012
    import nuke, re, os, time, pwd
        
    node = nuke.toNode("this")
    knobdata = node.writeKnobs(nuke.TO_SCRIPT)
    knobdata = re.sub("}", "", knobdata)
    knobdata = re.sub(" {", "", knobdata)
    knobdata = re.sub("{", "", knobdata)
    output = "Info for node: %s" % node.fullName()
    if node.channels(): 
        output+= "\n%s" % node.channels()
    for knob in list(node.knobs().keys()):
        if node[knob].Class() == "File_Knob":
            file_name= node[knob].evaluate()
            if file_name:
                magoutput= "" #set up ImageMagick output
                #if we have metadata, use it
                metadata_output= ""#in case of file problems
                if node.metadata():
                    #if frame is past end of sequence, will return 'file doesn't exist', so:
                    file_name= node.metadata()['input/filename']
                    metadata_output= "\n==================================================\nMetadata:\n"
                    for metakey, metavalue in list(node.metadata().items()):
                        metadata_output+= ("%s: %s\n")%(metakey, metavalue)

                #print the filename
                output+= "\n==================================================\n"
                output+= "%s:\n%s\n"%(node[knob].name(), file_name)
                #STAT the file
                #try:
                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)= os.stat(file_name)
                try:
                    if pwd.getpwuid(uid)[4]:
                        username= pwd.getpwuid(uid)[4]
                    else:
                        username= pwd.getpwuid(uid)[0]
                except (ImportError, KeyError):
                    username= "(uid: %s)" % uid
                output+= "\nOwned by %s" % username

                try:
                    output+= "\n%s (%s bytes)" % (sizeof_fmt(size),size)
                except: 
                    pass
                #print "last accessed: %s" % time.ctime(atime)
                try:
                    output+= "\nLast modified: %s" % time.ctime(mtime)
                except:
                    pass
                #print "created: %s" %time.ctime(ctime)

                #get ImageMagick info
                magoutput+= "\n==================================================\nImageMagick info:\n"
                #try:
                for line in runProcess(['identify', '-verbose', file_name]):
                        magoutput+= line
                #except:
                #    magoutput+= "not available: ImageMagick not installed, or not an image file?"
                #except:
                #    output += "\nFile error! Maybe file doesn't exist?"

                #print the metadata
                if metadata_output:
                    output+= metadata_output
            
                #print ImageMagick info
                output+= magoutput

    output+= "\n==================================================\n"
    output+= "\n" + nuke.showInfo()
    output+= "\n==================================================\n"
    output+= "\nKnob Info:"
    output+= "\n" + knobdata
    return output



if __name__ == "__main__":
    #runs when testing:
    multiple_node_info() 
else:
    #replace builtin Nukescripts with version above:
    oldnukescriptsinfoviewer= nukescripts.infoviewer
    nukescripts.infoviewer= multiple_node_info

