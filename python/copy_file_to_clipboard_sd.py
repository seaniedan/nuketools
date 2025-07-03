#fixed for Nuke 11

import nuke
from collections import defaultdict

def copy_to_clipboard(clipboard_text):
    """
    copy text to copy buffer
    fixed for nuke 11
    :param clipboard_text: str
    :return: none
    """
    # Try PySide6 first, then PySide2, then PySide
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QGuiApplication
    except ImportError:
        try:
            from PySide2.QtWidgets import QApplication
            from PySide2.QtGui import QGuiApplication
        except ImportError:
            from PySide.QtGui import QApplication
            QGuiApplication = QApplication  # Fallback for old PySide
    
    try:
        app = QApplication.instance()  # checks if QApplication already exists 
    except: 
        # create QApplication if it doesnt exist 
        import sys
        app = QApplication(sys.argv)

    clipboard = QGuiApplication.clipboard() 
    clipboard.setText(str(clipboard_text))


def clipboard_text():
    """
    returns text from copy buffer
    fixed for nuke 11
    :param clipboard_text: str
    :return: none
    """
    # Try PySide6 first, then PySide2, then PySide
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QGuiApplication
    except ImportError:
        try:
            from PySide2.QtWidgets import QApplication
            from PySide2.QtGui import QGuiApplication
        except ImportError:
            from PySide.QtGui import QApplication
            QGuiApplication = QApplication  # Fallback for old PySide

    try:
        app = QApplication.instance()  # checks if QApplication already exists 
    except: 
        # create QApplication if it doesnt exist 
        import sys
        app = QApplication(sys.argv)

    clipboard = QGuiApplication.clipboard() 
    return clipboard.text()



def find_text(nodes, allowed_knobs= ["File_Knob", "Multiline_Eval_String_Knob"]):#,sort= None'Ask'/'Class'/'Node'):
    ############################
    #creates a dictionary of node, knob objects and value
    #copy selected node paths/text to clipboard
    #by Sean Danischevsky 2014
    #TO DO: ask if you want to evaluate expressions?(n.b. if 'has expression': doesn't work...!)

    import os
    #if the text comes from the same class of node and knob name,
    #copy the list as an alphabetically sorted list
    #else sort by each class/knob name:
    #
    #Read nodes, file:
    #/that/file
    #/this/other/file
    #
    #Read nodes, label:
    #that thing I wrote
    #
    #Read nodes, proxy:
    #that/proxy/file
    #
    #Backdrop nodes, label:
    #this other thing I wrote
    #
    #
    #I do it this way rather than 'text:node_label' so I can sort by node later if i want to
    #e.g.
    #Read1
    #File: /this/one
    #Proxy: /that one
    #label: good
    #
    #Read2
    #File 'another/file'
    #

    node_class_label_text= defaultdict(set)  #can have more than one knob per node
    #dict {node:(class, label, text)}
    for node in nodes:
        #node[class_label_text] = defaultdict(list)
        knobs= node.knobs()
        for knob in list(knobs.keys()):
            if node[knob].Class()in allowed_knobs:
                vall= node[knob].value()
                if vall:
                    if ("[" in vall) and ("]" in vall):
                        #as [tcl] doesn't open in browsers, and isn't useful:
                        vall= node[knob].evaluate() 
                        #could do more here to put back %04d, #### ...

                    if node[knob].Class() == "File_Knob":
                        vall= os.path.abspath(vall) 

                    class_label_text= (node.Class(), node[knob].name(), vall)
                    node_class_label_text[node].add(class_label_text)
    return node_class_label_text




def copy_text_to_clipboard(nodes):        
    #copy to clipboard

    node_class_label_text= find_text(nodes, allowed_knobs= ["File_Knob", "Multiline_Eval_String_Knob", "EvalString_Knob"])

    #hold the text
    text= []

    if list(node_class_label_text.values()):
        #work out if we have only one class/label combination
        #class_label= [(v[0], v[1]) for v in node_class_label_text.values()]
        #[t[2] for t in [item for sublist in a.values() for item in sublist]]


        class_label= [(v[0], v[1]) for v in [item for sublist in list(node_class_label_text.values()) for item in sublist]]

        class_label= set(class_label)
        if len(class_label)> 1:
            #more than one class of node/label.
            #arrange by class, label, text:
            #print node_class_label_text
            '''d={}
            for path in node_class_label_text.values():
                current_level = d
                for part in path:
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]
            print d'''
            
            class_label= defaultdict(set)
            #dict of {'class nodes, label':[value, value, value]}
            for c, l, t in [item for sublist in list(node_class_label_text.values()) for item in sublist]:
                #print c,l,t
                k= c+ ' nodes, '+ l   #'Read nodes, file'
                class_label[k].add(t)

            #print class_label
            #text= [v[2] for v in [item for sublist in node_class_label_text.values() for item in sublist]]
            #text= list(set(text))
            #text.sort()
            #print sorted(class_label.iteritems(), key= lambda (k,v): (k,v))
            for key, value in sorted(iter(list(class_label.items())), key= lambda k_v: (k_v[0],k_v[1])): #sort by class, label
                text.append("\n%s:\n%s" % (key, '\n'.join(sorted(value))))
            l= [value for value in list(class_label.values())]
            flat_list = [item for sublist in l for item in sublist]

            unique_entries= len(   set(   flat_list   )   )
        elif len(class_label) == 1:
            #just one class of node/label.
            #sort the text and remove duplicates!
            #print node_class_label_text
            text= [v[2] for v in [item for sublist in list(node_class_label_text.values()) for item in sublist]]
            text= list(set(text))
            text.sort()
            unique_entries= len(text)
        else:
            return

    if text:
        #new line for each file
        cb= '\n'.join([file for file in text])

    else:
        #copy the script name
        cb= nuke.scriptName()
        unique_entries= 1
    copy_to_clipboard(cb)

    print('----------------------------------------------------')
    print((clipboard_text())) # show current clipboard contents
    if unique_entries> 1:
        print(("unique entries: %d"% unique_entries))
    return


def open_dirs_in_browser(nodes):
    #grab file paths or text in selected nodes and attempt to 
    #open directories in system file browser
    #if no nodes selected, open the Nuke script directory

    import os
    if nodes:
        #we're just interested in files
        #WriteTank etc don't have file knobs, so we use nuke.filename instad of
        #node_class_label_text= find_text(nodes, allowed_knobs= ["File_Knob", "Multiline_Eval_String_Knob", "EvalString_Knob"])
        #text= [v[2] for v in [item for sublist in node_class_label_text.values() for item in sublist]]
        #to find the files we're using.
        text= [nuke.filename(node) for node in nodes]
        # Filter out None and empty values
        text= [t for t in text if t and t.strip()]
        
        if not text:
            nuke.alert("No valid file paths found in selected nodes!")
            return
            
        #dict {node:(class, label, text)}
        #hold the text
        #print node_class_label_text
        #files= [t for c, l, t in node_class_label_text.values()]
        text= list(set(text))
        text.sort()
        #files= [file for file in t]
        #for i, file in enumerate(files):
        #print i, file
    else:
        #copy the script name
        script_name = nuke.scriptName()
        if not script_name or not script_name.strip():
            nuke.alert("No script name available!")
            return
        text= [script_name]

    if text:
        #check the dirs
        dirs= [] #directories that exist
        no_dirs= []# d!irectories that don't exist!
        for file in text:
            try:
                if not file or not file.strip():
                    continue
                dirname= os.path.dirname(file)
                if dirname and os.path.isdir(dirname):
                    dirs.append(dirname)
                else:
                    no_dirs.append(dirname)
            except Exception as e:
                no_dirs.append(f"Error processing {file}: {str(e)}")
        dirs= list(set(dirs))

        if len(dirs)> 1:
            if nuke.ask("Do you want to open %d directories in the file browser?"% len(dirs)):
                for dir in dirs:
                    open_dir_in_browser(dir)
        elif len(dirs) == 1:
            open_dir_in_browser(dirs[0])
        else:
            nuke.alert("No valid directories found to open!")

        #warn if no directories were found
        no_dirs= list(set(no_dirs))
        if len(no_dirs)> 1:
            nuke.message("Couldn't find these directories:\n%s" % ("\n".join([dir for dir in no_dirs])))
        elif len(no_dirs) == 1:
            nuke.message("Couldn't find directory:\n%s" % ("\n".join([dir for dir in no_dirs])))
    else:
        nuke.alert("No valid file paths found!")
    return


    
def open_dir_in_browser(dir):
    import os, sys, subprocess

    if sys.platform == 'darwin':
        subprocess.run(['open', dir], check=False)

    elif sys.platform == 'win32':
        dir = dir.replace('/', os.sep)
        subprocess.run(['explorer', dir], check=False)

    elif sys.platform.startswith('linux'):
        try:
            subprocess.Popen(['gio', 'open', dir])
        except Exception:
            nuke.message("Can't find a file browser!\nTry adding one in open_dir_in_browser (copy_file_to_clipboard_sd.py)")
    return
