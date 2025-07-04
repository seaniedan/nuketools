import nuke

def open_dir_in_browser(dir):
    import os, sys, subprocess

    if sys.platform == 'darwin':
        subprocess.run(['open', dir], check=False)

    elif sys.platform.startswith('linux'):
        try:
            subprocess.Popen(['gio', 'open', dir])
        except Exception:
            try:
                subprocess.Popen(['xdg-open', dir])
            except Exception:
                try:
                    subprocess.Popen(['nautilus', dir])
                except Exception:
                    nuke.message("Can't find a file browser!\nTry adding one in open_dir_in_browser (copy_file_to_clipboard_sd.py)")

    elif sys.platform == 'win32':
        dir = dir.replace('/', os.sep)
        subprocess.run(['explorer', dir], check=False)
    
    return


def capture_viewer():
    import os
    import time

    #filename
    home= os.path.expanduser("~")
    dirname= os.path.join(home, "Pictures", "NukeScreenGrabs")
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    #try to use script name
    try:
        basename= os.path.splitext(os.path.basename(nuke.scriptName()))[0]
    except:
        basename= time.strftime('%Y_%m_%d__%H_%M', time.localtime((time.time())))
    
    #file diesn't exist
    filename= os.path.join(dirname, basename)+ '.jpg'
    i= 0
    while os.path.exists(filename):
        i+= 1
        #filename exists so use filename(2).jpg etc.
        filename= os.path.join(dirname, basename)+ '(%d).jpg'% (i)  

    #capture viewer
    nuke.activeViewer().node().capture(filename)

    #open_dir_in_browser(os.path.dirname(filename))
    open_dir_in_browser(dirname)

    #TODO:
    # add dialigue using filePath= nuke.getFilename('Save Snapshot', pattern="*.jpg", default="~/tesssst/test.jpg", favorites="image", type="save", multiple=False)
    # add jog or jpeg if it doesn't endwith
    # warn if another ext is used
    # make a save function

###########################
#run when testing:
if __name__ == "__main__":
    capture_viewer()