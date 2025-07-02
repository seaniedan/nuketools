import subprocess
import os
import nuke

def launchNukeX(x):

	nuke.scriptSave()

	my_env= os.environ.copy()
	cmd= [nuke.env['ExecutablePath']]
	if x:
		cmd.append('-nukex')
	script_name = nuke.root().knob('name').value()
	if script_name:
		cmd.append(script_name)
	print(' '.join(cmd))

	subprocess.Popen(cmd, shell=False, env=my_env)
	nuke.scriptExit()