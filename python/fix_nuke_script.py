#!/usr/bin/env python
 
import re
 
BADLAYERS =   [ """add_layer {depth depth.cc depth.ZNorm depth.Zselect}""",
                """add_layer {rgba rgba.water redguard1.glow}"""]
 
def show_message(msg, title="Fix Nuke Script"):
    try:
        import nuke
        nuke.message(msg)
    except Exception:
        print(msg)
 
def removeBadLayers(nukeTxt, results=''): 
    global BADLAYERS
    for badLayer in BADLAYERS:
        badLayerRe = re.compile(badLayer, re.M)
        s = badLayerRe.search(nukeTxt)
        elems = []
        if s:
            nukeTxt = badLayerRe.sub('', nukeTxt)
            results += 'Removed layer: %s\n' % badLayer
            elems = re.search('(?<={).*(?=})', badLayer, re.S).group()
            elems = elems.split()
            elems = [elem for elem in elems if '.' in elem]
 
            for elem in elems:
                removeMe = re.compile('-?'+elem)
                found = removeMe.findall(nukeTxt)
                if found:
                    results += 'Removing: %s\n' % removeMe.findall(nukeTxt)
                nukeTxt = removeMe.sub('', nukeTxt)
 
    if results:
        show_message(results)
    return nukeTxt
 
 
def removeEmptyBraces(nukeTxt, results=''):                    
    # Cleanup bad knob expression
    braces = re.compile('[\w]* \{\}')
    foundbraces = braces.findall(nukeTxt)
    if foundbraces:
        results += 'Removing; %s\n' % foundbraces
        nukeTxt = braces.sub('', nukeTxt)
 
    if results:
        show_message(results)
 
    return nukeTxt
 
 
def findLonesomeClones(nukeTxt, results=''):    
    CLONE   = re.compile(r'clone \$(C[0-9A-Za-z]+)')
    SET     = re.compile(r'set (C[0-9A-Za-z]+)')
    clones  = CLONE.findall(nukeTxt)
    sets    = SET.findall(nukeTxt)      
    fixed = 0
    for c in clones:
        if c not in sets:
            fixed += 1
            # then the clone is lonesome and needs to be fixed.
            nukeTxt = nukeTxt.replace('clone $%s {\n' % c, 'NoOp {\n name FIXME%01d\n tile_color 0xff0000ff\n' % fixed)    
            results += 'Fixed lonesome Clone. This node needs to be replaced. Renamed: FIXME%01d\n' % fixed  
 
    if results:
        show_message(results)
 
    return nukeTxt
 
def main():
    import shutil, sys
    import nuke
    import os
    from datetime import datetime

    def gui_message(msg):
        try:
            nuke.message(msg)
        except Exception:
            print(msg)

    # Check if we're running in Nuke GUI environment
    try:
        fIn = nuke.getFilename("Select Nuke script to fix", "*.nk*")
        if not fIn:
            gui_message("No file selected. Exiting.")
            return
        in_gui = True
    except:
        if len(sys.argv) != 2:
            sys.exit('You must specify a nuke file to cleanup')
        fIn = sys.argv[1]
        in_gui = False
    
    if not os.path.exists(fIn):
        gui_message(f"File not found: {fIn}")
        return
    
    # Read the file first to check for changes
    try:
        with open(fIn, 'r') as nukefile:
            nukeTxt = nukefile.read()
        original_text = nukeTxt
        
        # Process the text to see if there are changes
        processed_text = removeBadLayers(original_text)                                  
        processed_text = removeEmptyBraces(processed_text)                    
        processed_text = findLonesomeClones(processed_text)
        
        # Only create backup and save if there are actual changes
        if processed_text != original_text:
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M")
            base_name = os.path.splitext(fIn)[0]
            extension = os.path.splitext(fIn)[1]
            backup_path = f"{base_name}-bkp-{timestamp}{extension}"
            shutil.copy2(fIn, backup_path)
            gui_message(f"Backup created: {backup_path}")
            
            # Save the fixed file
            with open(fIn, 'w') as nukefile:
                nukefile.write(processed_text)
            gui_message(f"Script fixed and saved: {fIn}")
        else:
            gui_message("No issues found in the script.")
            
    except Exception as e:
        gui_message(f"Error processing file: {e}")
        return
 
if __name__ == '__main__':
    main() 