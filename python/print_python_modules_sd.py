def print_python_modules():
    #print Nuke paths (everywhere Nuke looks for scripts, gizmos etc)
    #sean danischevsky 2014
    import nuke
    import sys

    #build modules list

    p= nuke.Panel('Python Modules')
    p.addNotepad('', "\n".join( list(sys.modules.keys())))
    p.setWidth(1000)
    ret= p.show()
    #print msg

##################################
#runs when testing:
if __name__ == "__main__":
    print_python_modules()