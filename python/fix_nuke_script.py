#!/usr/bin/env python
 
import re
 
BADLAYERS =   [ """add_layer {depth depth.cc depth.ZNorm depth.Zselect}""",
                """add_layer {rgba rgba.water redguard1.glow}"""]
 
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
        print(results)
    return nukeTxt
 
 
def removeEmptyBraces(nukeTxt, results=''):                    
    # Cleanup bad knob expression
    braces = re.compile('[\w]* \{\}')
    foundbraces = braces.findall(nukeTxt)
    if foundbraces:
        results += 'Removing; %s\n' % foundbraces
        nukeTxt = braces.sub('', nukeTxt)
 
    if results:
        print("%s" % results)
 
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
        print("%s" % results)
 
    return nukeTxt
 
def main():
    import shutil, sys
    import nuke
    import os
 
    # Check if we're running in Nuke GUI environment
    try:
        # Try to get file from Nuke file dialog
        fIn = nuke.getFilename("Select Nuke script to fix", "*.nk *.nkx *.nknc")
        if not fIn:
            print("No file selected. Exiting.")
            return
    except:
        # Fallback to command line if not in Nuke
        if len(sys.argv) != 2:
            sys.exit('You must specify a nuke file to cleanup')
        fIn = sys.argv[1]
    
    # Verify file exists and is readable
    if not os.path.exists(fIn):
        print(f"File not found: {fIn}")
        return
    
    # Create backup
    backup_path = '%s.backup' % fIn
    shutil.copy2(fIn, backup_path)
    print(f"Backup created: {backup_path}")
    
    # Read and process the file
    try:
        with open(fIn, 'r') as nukefile:
            nukeTxt = nukefile.read()
        
        original_text = nukeTxt
        
        nukeTxt = removeBadLayers(nukeTxt)                                  
        nukeTxt = removeEmptyBraces(nukeTxt)                    
        nukeTxt = findLonesomeClones(nukeTxt)
        
        # Only write if changes were made
        if nukeTxt != original_text:
            with open(fIn, 'w') as nukefile:
                nukefile.write(nukeTxt)
            print(f"Script fixed and saved: {fIn}")
        else:
            print("No issues found in the script.")
            
    except Exception as e:
        print(f"Error processing file: {e}")
        return
 
if __name__ == '__main__':
    main() 