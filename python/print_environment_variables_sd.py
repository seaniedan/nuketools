def print_environment_variables():
    #print environment variables
    #sean danischevsky 2018
	import os
	import nuke
	#for k,v in sorted(os.environ.iteritems()):
	    #myline="%s: %s"%(k,v))
	msg= "\n".join(["%s: %s"%(k,v) for k,v in sorted(os.environ.items())])
	p= nuke.Panel('Environment Variables')
	p.addNotepad('Variables', msg)
	p.setWidth(1000)
	ret= p.show()

##################################
#runs when testing:
if __name__ == "__main__":
    print_environment_variables()