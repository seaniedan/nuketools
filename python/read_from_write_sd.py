import nuke
#For Nuke Write nodes, returns a Read node.
#if it's a read already/RELOAD the read. And check for expanded frame range.
#GenerateLUT -> Vectorfield
#WriteGeo -> ReadGeo
#Sean Danischevsky 2016 etc.


def VectorfieldFromNode(node):
    #node= nuke.nodes.Vectorfield()  #switched to ocio file transform
    #node['vfield_file'].setValue(filepath)  
    try:
        filepath= node['file'].value()
        v= nuke.nodes.OCIOFileTransform()
        v['file'].setValue(filepath)
        v.setXYpos(node.xpos(), node.ypos()+ node.screenHeight())
        return v
    except Exception as e:
        return e


def SmartVectorFromNode(node):
    try:
        filepath= node['file'].value()
        sv= nuke.nodes.SmartVector()
        sv['file'].setValue(filepath)
        sv.setXYpos(node.xpos(), node.ypos()+ node.screenHeight())    
        return sv
    except Exception as e:
        return e


def ReadGeoFromNode(node):
    try:
        filepath= node['file'].value()    
        rg= nuke.nodes.ReadGeo()
        rg['file'].setValue(filepath)
        rg.setXYpos(node.xpos(), node.ypos()+ node.screenHeight())    
        return rg
    except Exception as e:
        return e


def readFromFile(filepath):
    #should really use nuke.getFileNameList(os.path.dirname(os.path.abspath(filepath)))
    #but hey, this works:
    
    import os 
    import re

    movie_extensions= ['.qt', '.mov', '.mxf']
    dirpath, basepath= os.path.split(os.path.abspath(filepath)) 

    dirContents= nuke.getFileNameList(dirpath, False, False, False, False) #getFileNameList(dir, splitSequences= False, extraInformation= False, returnDirs=True, returnHidden=False)
    #print basepath
    #print dirContents
    base, extension= os.path.splitext(basepath)
    #remove spaces from extension - for 'None - None' problem in Shotgun/Nuke
    extension= re.sub(r' .+', '', extension)

    #print base, extension

    if extension in movie_extensions:
        return filepath

    matchstring, subs= re.subn(r'\d+$', '', base) #remove numbers from end, if any

    #replace . with \. to match literal . in filenames
    matchstring= re.sub(r'\.', '\.',matchstring)

    if subs:
        #there was a number at end
        #matchstring+= "\d" #add wildcard for numbers
        matchstring+= ".+" #add wildcard for numbers
    #add extension and xxx-yyy - maybe I could improve on '*'
    matchstring+= extension+ ".*"
    print(("matchstring: "+ matchstring))
    matches= [string for string in dirContents if re.match(matchstring, string)]
    print(("matches: ", matches))

    firstone= os.path.join(dirpath, matches[0])
    #node= nuke.createNode('Read')
    #node= nuke.nodes.Read()#faster
    #node['file'].fromUserText('%s' % (firstone))  #safest/easiest to do this way and not too slow.
    #node.setSelected(True) #I'll do this for all later
    #return r
    #r['reload'].execute()
    return firstone

    #except Exception as e:
    #    return e



def readFromWrite(node):
    #Creates a Read node for the selected Write node
    #Modifed by Sean Danischevsky 2017

    import re
    try:
        #filepath= node.knob('file').getValue()
        #this gets the evaluated value
        #i.e. returns a file with frame number like 
        # /mnt/..../file.1001.dpx
        filepath= nuke.filename(node, nuke.REPLACE)
        #check if nuke.REPLACE did anything? if not, just use filepath?
        #print 'filePath is: '+filePath
        r= nuke.nodes.Read() #faster
        r['file'].fromUserText('%s'% (readFromFile(filepath)))  #safest/easiest to do this way and not too slow.

        r.setXYpos(node.xpos(), node.ypos()+ r.screenHeight())
        #nuke.autoplaceSnap(r)




        #to do: check if this is default, and if so, do nothing
        #hacky way to set 'default linear'
        ###########read['colorspace'].setValue(nuke.getColorspaceList(read['colorspace'])[0])#######
        #used to set it as 'default' which stopped working, then
        #read['colorspace'].setValue(nuke.defaultColorspaceMapper('linear', nuke.FLOAT))

        colorspace= node['colorspace'].value()
        #print 'colorspace is: '+ str(colorspace)
        if r['colorspace'].value() != colorspace and colorspace != "default":
            #print r['colorspace'].value()        
            #r.knob('colorspace').setValue(colorspace.replace("default (", "").replace(")", ""))
            #should use lstrip, and rstrip only if lstrip was used.
            colorspace_matchstring= r"default \((.+)\)"
            m= re.match(colorspace_matchstring, colorspace)
            if m:
                colorspace= m.group(1) 
            #colorspace= colorspace.lstrip("default (".rstrip(")"))
        
            r['colorspace'].setValue(colorspace)
        return r #nuke node

    except Exception as e:
        return e #exception



def updateRead(node):
    #aka readfromreads
    import re
    import os 
    #print 'UPDATE READ'
    filepath= nuke.filename(node, nuke.REPLACE)

    movie_extensions= ['.qt', '.mov', '.mxf']
    
    dirpath, basepath= os.path.split(os.path.abspath(filepath)) 
    dirContents= nuke.getFileNameList(dirpath, False, False, False, False) #getFileNameList(dir, splitSequences= False, extraInformation= False, returnDirs=True, returnHidden=False)

    base, extension= os.path.splitext(basepath)
    #print base, extension
    #remove spaces from extension - for 'None - None' problem in Shotgun/Nuke
    extension= re.sub(r' .+', '', extension)

    if extension in movie_extensions:
        node['file'].fromUserText('%s'% (filepath))  #safest/easiest to do this way and not too slow.
        #print "video"
        return node

    matchstring, subs= re.subn(r'\d+$', '', base) #remove numbers from end, if any

    #replace . with \. to match literal . in filenames
    matchstring= re.sub(r'\.', '\.',matchstring)

    if subs:
        #there was a number at end
        #matchstring+= "\d" #add wildcard for numbers
        matchstring+= ".+" #add wildcard for numbers
    #add extension and xxx-yyy - maybe I could improve on '*'
    matchstring+= extension+ ".*"
    matches= [string for string in dirContents if re.match(matchstring, string)]
    if matches:
        firstone= os.path.join(dirpath, matches[0])
        #print "first one"
        node['file'].fromUserText('%s' % (firstone))  #safest/easiest to do this way and not too slow.

    node['reload'].execute()

    return node



def readFromWrites(nodes):
    #import time
    #t0 = time.time()
    #timed code block:
    unsucessful= []
    return_nodes= []
    for node in nodes:
        if node.Class() in ['Write', 'WriteTank']:# need my recursive read dictionary here
            return_result= readFromWrite(node) 
        elif node.Class() in ['GenerateLUT']:
            return_result= VectorfieldFromNode(node)
        elif node.Class() in ['SmartVector']:
            return_result= SmartVectorFromNode(node) 
        elif node.Class() in ['WriteGeo']:
            return_result= ReadGeoFromNode(node)              
        elif node.Class() in ['Read']: 
            return_result = updateRead(node) 

        else:
            #try it anyway 
            #would be nice to return the right reader for each file type, like in recursive read.
            return_result= readFromWrite(node)

        if not isinstance(return_result, nuke.Node):
            #it didn't work
            unsucessful.append(return_result)
        else:
            return_nodes.append(return_result)
    #really want to check for missing frames here and report            
    if unsucessful:
        #no_frames_msg= "Couldn't find any rendered frames in\n%s"% ("\n".join(dirpath for dirpath in unsucessful if dirpath is string))
        #no_dirs_msg= "Couldn't find any rendered frames in\n%s"% ("\n".join(dirpath for dirpath in unsucessful if dirpath is string))
        #msg="\n".join(dirpath for dirpath in unsucessful)
        #msg="\n".join('%s'%dirpath for dirpath in unsucessful)
        pass
        #return# nuke.message(msg)
    #end timed code block
    #t1= time.time()
    #total= t1-t0
    #print nuke.selectedNode().name()+": "+ str(total)+' seconds.'
    #.7 or .8 secs first time then .07
    return return_nodes