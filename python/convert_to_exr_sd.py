import nuke
def convert_to_exr(reads= nuke.selectedNodes("Read")):
    ################################
    #convertToEXR
    #by Sean Danischevsky 2011
    #2013 - v1.1 - added colorspace and retime checks
    #
    #to do:
    #
    #v1.2: 
    #if range, put exrs in 'exr' directory - or '../exr' ...?
    #
    #v1.3 - if not a read node, go up the tree to find the topnode and leave writes.
    #leaveWrite=True
    #
    #v2: add 'gui=True' option, for a dialogue box:
    #    show render range, add 'render' button
    #    'keep writes' checkbox
    #    only warn once if exrs exist: add 'no to all' and 'yes to all' buttons.
    
    import os
    
    if not reads: 
      nuke.message("Select some Read nodes from which to create EXRs.") 
      return
    #oldfile=[]
    count= 0
    for read in reads:
        oldfile= read['file'].value()
        first= read['origfirst'].value()
        last= read['origlast'].value()
        oldfileSplit= oldfile.split(".")
        extension= oldfileSplit[-1]
        if extension!= "exr":
            count+= 1
            newfileSplit= oldfileSplit[:-1]
            newfileSplit.append("exr")
            newfile= ".".join(newfileSplit)
            ###CHECK IF EXR ALREADY EXISTS
            #single frame
            exrExists= False
            if os.path.exists(newfile):
                exrExists= True
            else:
                #evaluate for multiple frames
                for f in range (first, last+1):
                    try:
                        print(((newfile)%f))
                        if os.path.exists((newfile)%f):
                            exrExists= True
                            break
                    except:
                        break
            #delete and remake?
            #keep_writes = nuke.ask("Just create write nodes and don't render?") 
            #keep_reads = nuke.ask("Just create write nodes and don't render?") 
            if exrExists:
                msg= "An EXR version already exists for\n%s\nOverwrite?" % (oldfile)
                delete_existing_file= nuke.ask(msg)
            if (not exrExists) or (exrExists and delete_existing_file):
                #create write node
                write= nuke.nodes.Write()
                write['file'].setValue(newfile)
                write['channels'].setValue('all')
                write['file_type'].setValue('exr')
                write['autocrop'].setValue(True)
                write['first'].setValue(first)
                write['last'].setValue(last)
                write['use_limit'].setValue(True)

                #test for retiming 
                retiming= (read['first'].value()!= first) or (read['last'].value()!= last) or (read['frame_mode'].value()== 'expression' and read['frame'].value()) or (read['frame_mode'].value()!='expression')
                if retiming:
                    #bring in a tempRead for such occasions
                    tempRead= nuke.createNode("Read")
                    tempRead['file'].setValue(oldfile)
                    tempRead['format'].setValue(read['format'].value())
                    tempRead['first'].setValue(first)
                    tempRead['last'].setValue(last)
                    tempRead['origfirst'].setValue(first)
                    tempRead['origlast'].setValue(last)
                    tempRead['colorspace'].setValue(read['colorspace'].value())
                    tempRead['premultiplied'].setValue(read['premultiplied'].value())
                    tempRead['raw'].setValue(read['raw'].value())
                    write.setInput(0, tempRead)
                else:
                    write.setInput(0, read)
                ###render###
                nuke.execute(write, first, last, 1)
                print((write['file'].value(), first, last))
                # replace the old read with the exr
                read['file'].setValue(newfile)
                #hacky way to set 'default linear'
                read['colorspace'].setValue(nuke.getColorspaceList(read['colorspace'])[0])
                #used to set it as 'default' which stopped working, then
                #read['colorspace'].setValue(nuke.defaultColorspaceMapper('linear', nuke.FLOAT))
                # delete the write node
                nuke.delete(write)
                # delete the temp read
                if retiming:
                    nuke.delete(tempRead)
            else:
                break
    if not count:
        #no files were converted!
        nuke.message("Couldn't convert any Read nodes to EXRs!\nSelected a non-EXR format image.") 
    return

###########################
#runs when testing:
if __name__ == "__main__":
    convert_to_exr(nuke.selectedNodes("Read"))
