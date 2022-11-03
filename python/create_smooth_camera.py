#need to do smooth_translate x,y separately for translate nodes

import nuke

def main(nodes= nuke.selectedNodes()):
    """
    creates a duplicate camera smooth tabs
    :param: None
    :return: None
    """

    classtypes = ['Camera' , 'Camera2', 'CornerPin2D','Transform']
    nodes = [node for node in nodes if node.Class() in classtypes]
    if nodes:
        for node in nodes:
            for i in nuke.selectedNodes():
                i['selected'].setValue(False) # deselect all selected nodes
            node['selected'].setValue(True) # select camera
            nuke.nodeCopy('%clipboard%') # copy camera
            node['selected'].setValue(False) # deselect camera, so it doesn't get pasted inline
            smooth_camera = nuke.nodePaste('%clipboard%') # create smooth camera
            xposd = node.xpos()+ node.screenWidth()/ 2  
            yposd = node.ypos()
            smooth_camera.setXYpos(xposd+ 100, yposd) # move smooth_camera next to original camera
            try:
                smooth_camera['name'].setValue(node['name'].getValue() + '_smoothed')
                smooth_camera['read_from_file'].setValue(False) # disable read from file or it won't allow changing curves
            except:
                pass

            #add knobs
            k = nuke.Tab_Knob('Smooth_sd')
            k.setTooltip("Smooth Camera movement by Sean Danischevsky 2018")
            smooth_camera.addKnob(k)
            k = nuke.Double_Knob('smooth_t', 'smooth translation') # add float knobs for smoothing translation
            k.setRange(0, 20)
            k.setValue(1) # default value
            k.setTooltip("Smooth translation over this many frames")
            smooth_camera.addKnob(k)

            if node.Class() in ['Camera', 'Camera2','Transform']:
                k = nuke.Double_Knob('smooth_r', 'smooth rotation') # add float knobs for smoothing rotation
                k.setRange(0, 20)
                k.setValue(1)
                k.setTooltip("Smooth rotation over this many frames")
                smooth_camera.addKnob(k)

                k = nuke.Double_Knob('smooth_s', 'smooth scale') # add float knobs for smoothing rotation
                k.setRange(0, 20)
                k.setValue(1)
                k.setTooltip("Smooth scale over this many frames")
                smooth_camera.addKnob(k)

            '''try:
                smooth_camera['User'].setLabel('Smoothing') # rename 'User' tab that gets created   
            except:
                #the user has already added custom knobs, and renamed the 'user' tab...
                pass '''

            #add smoothing expressions           
            camera_name = node['name'].getValue()

            if node.Class() in ['Camera' , 'Camera2']:
                smooth_camera['translate'].setExpression(camera_name+'.translate.x.animated==0?'+camera_name+'.translate.x:'+camera_name+ '.translate.x.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',0)
                smooth_camera['translate'].setExpression(camera_name+'.translate.y.animated==0?'+camera_name+'.translate.y:'+camera_name+ '.translate.y.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',1)
                smooth_camera['translate'].setExpression(camera_name+'.translate.z.animated==0?'+camera_name+'.translate.z:'+camera_name+ '.translate.z.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',2)
                smooth_camera['rotate'].setExpression(camera_name+'.rotate.x.animated==0?'+camera_name+'.rotate.x:'+camera_name+ '.rotate.x.integrate(frame-max(smooth_r,0.00001),frame+max(smooth_r,0.00001))/(2*max(smooth_r,0.00001))',0)
                smooth_camera['rotate'].setExpression(camera_name+'.rotate.y.animated==0?'+camera_name+'.rotate.y:'+camera_name+ '.rotate.y.integrate(frame-max(smooth_r,0.00001),frame+max(smooth_r,0.00001))/(2*max(smooth_r,0.00001))',1)
                smooth_camera['rotate'].setExpression(camera_name+'.rotate.z.animated==0?'+camera_name+'.rotate.z:'+camera_name+ '.rotate.z.integrate(frame-max(smooth_r,0.00001),frame+max(smooth_r,0.00001))/(2*max(smooth_r,0.00001))',2)
                smooth_camera['scaling'].setExpression(camera_name+'.scaling.x.animated==0?'+camera_name+'.scaling.x:'+camera_name+ '.scaling.x.integrate(frame-max(smooth_s,0.00001),frame+max(smooth_s,0.00001))/(2*max(smooth_s,0.00001))',0)
                smooth_camera['scaling'].setExpression(camera_name+'.scaling.y.animated==0?'+camera_name+'.scaling.y:'+camera_name+ '.scaling.y.integrate(frame-max(smooth_s,0.00001),frame+max(smooth_s,0.00001))/(2*max(smooth_s,0.00001))',1)
                smooth_camera['scaling'].setExpression(camera_name+'.scaling.z.animated==0?'+camera_name+'.scaling.z:'+camera_name+ '.scaling.z.integrate(frame-max(smooth_s,0.00001),frame+max(smooth_s,0.00001))/(2*max(smooth_s,0.00001))',2)

            elif node.Class() in ['CornerPin2D']:
                smooth_camera['to1'].setExpression(camera_name+'.to1.x.animated==0?'+camera_name+'.to1.x:'+camera_name+ '.to1.x.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',0)
                smooth_camera['to1'].setExpression(camera_name+'.to1.y.animated==0?'+camera_name+'.to1.y:'+camera_name+ '.to1.y.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',1)
                smooth_camera['to2'].setExpression(camera_name+'.to2.x.animated==0?'+camera_name+'.to2.x:'+camera_name+ '.to2.x.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',0)
                smooth_camera['to2'].setExpression(camera_name+'.to2.y.animated==0?'+camera_name+'.to2.y:'+camera_name+ '.to2.y.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',1)     
                smooth_camera['to3'].setExpression(camera_name+'.to3.x.animated==0?'+camera_name+'.to3.x:'+camera_name+ '.to3.x.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',0)
                smooth_camera['to3'].setExpression(camera_name+'.to3.y.animated==0?'+camera_name+'.to3.y:'+camera_name+ '.to3.y.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',1)
                smooth_camera['to4'].setExpression(camera_name+'.to4.x.animated==0?'+camera_name+'.to4.x:'+camera_name+ '.to4.x.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',0)
                smooth_camera['to4'].setExpression(camera_name+'.to4.y.animated==0?'+camera_name+'.to4.y:'+camera_name+ '.to4.y.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',1)            
     
            elif node.Class() in ['Transform']:
                smooth_camera['translate'].setExpression(camera_name+'.translate.x.animated==0?'+camera_name+'.translate.x:'+camera_name+ '.translate.x.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',0)
                smooth_camera['translate'].setExpression(camera_name+'.translate.y.animated==0?'+camera_name+'.translate.y:'+camera_name+ '.translate.y.integrate(frame-max(smooth_t,0.00001),frame+max(smooth_t,0.00001))/(2*max(smooth_t,0.00001))',1)
                smooth_camera['rotate'].setExpression(camera_name+'.rotate.animated==0?'+camera_name+'.rotate:'+camera_name+ '.rotate.integrate(frame-max(smooth_r,0.00001),frame+max(smooth_r,0.00001))/(2*max(smooth_r,0.00001))',0)
                smooth_camera['scale'].setExpression(camera_name+'.scale.animated==0?'+camera_name+'.scale:'+camera_name+ '.scale.integrate(frame-max(smooth_s,0.00001),frame+ max(smooth_s,0.00001))/(2*max(smooth_s,0.00001))',0)
                #smooth_camera['scale'].setExpression(camera_name+'.scale.y.animated==0?'+camera_name+'.scale.y:'+camera_name+ '.scale.y.integrate(frame-max(smooth_s,0.00001),frame+ max(smooth_s,0.00001))/(2*max(smooth_s,0.00001))',1)

    else:
        nuke.message("No usable nodes selected!\nPlease select one or more %s nodes to add a smooth tab."%"/".join(classtypes))
    return

if __name__ == '__main__':
    main()
