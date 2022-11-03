import nuke #this has to be out of the def if you set 'node=nuke.thisnode' as a default.

def write_mkdir(node= None, askUser= False):
    # CREATE MISSING DIRECTORIES FOR WRITE NODES and other classes.
    # used as a callback on Write nodes.
    # by Sean Danischevsky 2014
    # must set node to None in the def, so we can use in callbacks, where passing args isn't allowed.
    # if I set it to nuke.thisNode in the def, it passes 'root', which fails.
    import os

    if not node: #nuke.thisNode fails to return anything when set in the def, and called as a callback.
        node= nuke.thisNode()
    try:
        path= node['file'].evaluate()
    except Exception as e:
        nuke.message("Couldn't evaluate 'file' for node\n%s\n%s" % (node.name(), e))
        return

    if path:
        dirPath = os.path.normpath(os.path.dirname(path))
        if os.path.isdir (dirPath):
            #the directory exists already! :-)
            return 
        
        elif os.path.isfile (dirPath):
            # The directory path exists, but is a file!
            return nuke.message("The directory:\n%s\nexists as a file." % (dirPath))

        if askUser:
            # Ask if we want to create the directory
            delete_existing_file= nuke.message(msg)
            msg= "Create this directory?\n%s"%(("\n").join(dirsNeeded))
            createDirs = nuke.ask(msg)
            if not createDirs:
                return

        #all good to make the dir
        try:
            os.makedirs(dirPath) #was (dirPath, 0775)
            print(('Created directory', dirPath))
        except Exception as e:
            nuke.message("Couldn't create directory\n%s\n%s" % (dirPath, e))
            return