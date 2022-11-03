#autosave_sd.py
#keep the line above!
###############################
# autosave_sd
# by Sean Danischevsky 2011
# sean@seandanischevsky.com
#
# Wrote this to replace TCL autosave: 
# [file dirname [firstof [value root.name] [getenv NUKE_TEMP_DIR]/]]/.[file tail [firstof [value root.name] untitled]].autosave[clock seconds]

#user defined global variable. 10 should be enough but lets set...
max_autosave_files= 33
import nuke #yep, you really need to import it :-)

def autosave_sd_name_format(autosavedir, autosavebase, autosavenumber):
     import os
     #return os.path.join(autosavedir, (".%s%04d.nk")%(autosavebase.replace(".nk","")  ,autosavenumber))
     #return os.path.join(autosavedir, ("%s.nk%04d")%(autosavebase.replace(".nk","")  ,autosavenumber))
     return os.path.join(autosavedir, ("%s%04d")%(autosavebase, autosavenumber))

def autosave_sd_this(source, dest):
    import shutil
    try:
        shutil.copyfile(source, dest) 
        nuke.tprint(('Copied %s to %s')%(source, dest))
        print((('Copied %s to %s')%(source, dest)))
    except:
        nuke.message(('Couldnt copy %s to %s')%(source, dest))
        nuke.tprint(('Couldnt copy %s to %s')%(source, dest))
    return

def autosave_sd():
    import os
    #get Nuke autosave file name
    autosave_file= nuke.toNode("preferences")["AutoSaveName"].evaluate()
    #If no existing Nuke autosave files:
    if not os.path.exists(autosave_file):
        print("No autosave file to backup.")
        return
    else:
        #figure out the autosave names
        autosavedir= os.path.dirname(autosave_file)
        autosavebase= os.path.basename(autosave_file)
        #remove leading '.' if it exists
        if autosavebase[0]=='.':
            autosavebase= autosavebase[1:]
        #loop through saved autosave files. 
        for i in range(max_autosave_files):
            autosave_sd= autosave_sd_name_format(autosavedir, autosavebase, i)
            #print ("Looking for %s")%(autosave_sd)
            if os.path.exists(autosave_sd):
                #the autosave exists
                #print ("%s exists")%(autosave_sd)
                if i== max_autosave_files- 1:
                    #we reached the max! 
                    #print "We reached the max!"
                    #loop through all files, copy over oldest!
                    autosave_sds= [(os.path.getmtime(autosave_sd_name_format(autosavedir, autosavebase, f)), autosave_sd_name_format(autosavedir, autosavebase, f)) for f in range(max_autosave_files)]
                    #print autosave_sds
                    autosave_sd_this(autosave_file, min(autosave_sds)[1])
                    return
                else:
                #carry on until max_autosave_files
                    continue
            else: 
                #reached an empty slot: save the autosave here
                autosave_sd_this(autosave_file,autosave_sd)
                return

#unhash next line to test
#autosave_sd()

#ADD AUTOSAVE
#for some reason this must be done in menu.py
#nuke.addOnScriptSave(seanscripts.autosave_sd)
#unhash next line to test
#m_autosave()


                      
