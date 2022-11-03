import subprocess
import os
import nuke

def launchNukeX(x):

	nuke.scriptSave()

	my_env= os.environ.copy()
	cmd= nuke.env['ExecutablePath']
	if x:
		cmd+= " -nukex"
	cmd += " "
	cmd += nuke.root().knob('name').value()
	print(cmd)

	subprocess.Popen(cmd, shell= True, env= my_env)
	nuke.scriptExit()