def print_nuke_paths():
    #print Nuke paths (everywhere Nuke looks for scripts, gizmos etc)
    #sean danischevsky 2014
    import nuke
    import os

    #build path list
    msg= []
    for dir in nuke.pluginPath():
       if os.path.exists(dir):
            files= os.listdir(dir)
            if files:
                for file in files:
                    msg.append(os.path.join(dir, file))
            else: 
                msg.append("* EMPTY DIRECTORY: %s"% dir)
       else:
            msg.append("* MISSING DIRECTORY: %s"% dir)

    p= nuke.Panel('Nuke Paths')
    p.addNotepad('Paths', "\n".join(msg))
    p.setWidth(1000)
    ret= p.show()
    #print msg

##################################
#runs when testing:
if __name__ == "__main__":
    print_nuke_paths()