#label defaults

import nuke, os

'''
non-autolabel example
nuke.knobDefault("Tracker3.label","[value transform] [value reference_frame]")
'''

#Tracker3 (old tracker): show what it's doing
def Tracker3Autolabel():
    ll= nuke.thisNode().name()
    xform= nuke.thisNode()['transform'].value()
    ll+= "\n%s, %d"%(xform,nuke.thisNode()['reference_frame'].value())
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+nuke.thisNode()['label'].evaluate()
    return ll

nuke.addAutolabel(Tracker3Autolabel, nodeClass= 'Tracker3')
nuke.addAutolabel(Tracker3Autolabel, nodeClass= 'Tracker4')


#Ramp: show whether vertical, horizontal, or diagonal
def RampAutolabel():
    ll= nuke.thisNode().name()
    if nuke.thisNode()['p0'].value() == nuke.thisNode()['p1'].value():
        ll+= "\n(point)"
    elif abs(nuke.thisNode()['p0'].value()[0]- nuke.thisNode()['p1'].value()[0]) == abs(nuke.thisNode()['p0'].value()[1]- nuke.thisNode()['p1'].value()[1]):
        ll+= "\n(diagonal)"
    elif nuke.thisNode()['p0'].value()[0] == nuke.thisNode()['p1'].value()[0]:
        ll+= "\n(vertical)"
    elif nuke.thisNode()['p0'].value()[1] == nuke.thisNode()['p1'].value()[1]:
        ll+= "\n(horizontal)"
    elif nuke.thisNode()['p0'].value()[0]- nuke.thisNode()['p1'].value()[0]< nuke.thisNode()['p0'].value()[1]- nuke.thisNode()['p1'].value()[1]:
        ll+= "\n(sort of horizontal)"
    elif nuke.thisNode()['p0'].value()[0]- nuke.thisNode()['p1'].value()[0]> nuke.thisNode()['p0'].value()[1]- nuke.thisNode()['p1'].value()[1]:
        ll+= "\n(sort of vertical)"
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+ nuke.thisNode()['label'].evaluate()
    return ll

nuke.addAutolabel(RampAutolabel, nodeClass= 'Ramp')

#Constant: show format name
def ConstantAutolabel():
    ll= nuke.thisNode().name()
    if nuke.thisNode().format().name():
        ll+= "\n%s"%(nuke.thisNode().format().name())
    else:
        ll+= "\n%dx%d"%(int(nuke.thisNode().format().width()),int(nuke.thisNode().format().height()))
        #don't think aspect can be changed from 1 if it hasn't been created by user
        #(and therefore will have a name), so hashed this:
        #if nuke.thisNode().format().pixelAspect()!=1:
            #ll+="(aspect %d)"%(nuke.thisNode().format().pixelAspect())
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+ nuke.thisNode()['label'].evaluate()
    return ll
nuke.addAutolabel(ConstantAutolabel, nodeClass= 'Constant')

#Inputs: show index
#if making a group and inputs get messed up, delete all inputs and
#create an Input called 'Input0' (you may need to copy and paste the node).
nuke.knobDefault('Input.label', '(input [value number])')

#FrameBlend: show value or number of frames
def FrameBlendAutolabel():
    ll= nuke.thisNode().name()
    if nuke.thisNode()['userange'].value():
        ll+= "\nframes %d-%d"%(nuke.thisNode()['startframe'].value(),nuke.thisNode()['endframe'].value())
    else:
        ll+= "\n%d frames"%(nuke.thisNode()['numframes'].value())
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+nuke.thisNode()['label'].evaluate()
    return ll

#nuke.knobDefault("FrameBlend.label","[? userange frames [value startframe]-[value endframe] [value numframes] frames]")
nuke.addAutolabel(FrameBlendAutolabel, nodeClass= 'FrameBlend')

#Truelight: show profile
#nuke.knobDefault("Truelight3.label","[getenv TL_PROFILE]")

#Colorspace: show operation
def colorspaceAutolabel():
    ll= nuke.thisNode().name()
    ll+= "\n%s -> %s"% (nuke.thisNode()['colorspace_in'].value(),nuke.thisNode()['colorspace_out'].value())
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+nuke.thisNode()['label'].evaluate()
    return ll

#nuke.knobDefault("FrameBlend.label","[? userange frames [value startframe]-[value endframe] [value numframes] frames]")
nuke.addAutolabel(colorspaceAutolabel, nodeClass='Colorspace')

#Write: if render range set, show it.
#would be nice to find out what __autolabel.py__ applies to this and check my version is the same
def writeAutolabel():
    ll= nuke.thisNode().name()
    if nuke.thisNode()['file'].value():
        ll+= "\n%s"%(os.path.basename(nuke.thisNode()['file'].evaluate()))
    if nuke.thisNode()['use_limit'].value():
        ll+= "\nrange: %d-%d"%(nuke.thisNode()['first'].value(),nuke.thisNode()['last'].value())
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+ nuke.thisNode()['label'].evaluate()
    return ll

nuke.addAutolabel(writeAutolabel, nodeClass='Write')

#FrameRange: show clip range and calculate length
def FrameRangeAutolabel():
    ll= nuke.thisNode().name()
    ll+= "\n%d-%d\n(%d frames)"%(nuke.thisNode()['first_frame'].value(),nuke.thisNode()['last_frame'].value(),abs(nuke.thisNode()['last_frame'].value()-nuke.thisNode()['first_frame'].value())+1)
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+ nuke.thisNode()['label'].evaluate()
    return ll

nuke.addAutolabel(FrameRangeAutolabel, nodeClass='FrameRange')


#OCIOCDLTransform, Camera, Axis, : show filename if using file
def fileAutolabel():
    ll=nuke.thisNode().name()
    if nuke.thisNode()['read_from_file'].value():
        try:
            ll+= "\n%s"% (os.path.basename(nuke.thisNode()['file'].evaluate()))
        except:
            ll+= "\nno file selected"
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+ nuke.thisNode()['label'].evaluate()
    return ll

for nodeClass in ['OCIOCDLTransform', 'Axis2', 'Camera2']:
    nuke.addAutolabel(fileAutolabel, nodeClass=nodeClass)


#Vectorfield2: show filename 
def VectorfieldAutolabel():
    ll= nuke.thisNode().name()
    if nuke.thisNode()['vfield_file'].value():
        try:
            ll+= "\n%s"% (os.path.basename(nuke.thisNode()['vfield_file'].evaluate()))
        except:
            ll+= "\nno file selected"
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+ nuke.thisNode()['label'].evaluate()
    return ll

nuke.addAutolabel(VectorfieldAutolabel, nodeClass='Vectorfield')


#TimeOffset: show value, 
#to do 
#warn if beyond clip length:
#set tile_color or label?
#e.g. -45 (10 frames held at end)
#tricky with x Reverse option etc
#...and other time issues?
def TimeOffsetAutolabel():
    ll= nuke.thisNode().name()
    ll+= "\n%d"%nuke.thisNode()['time_offset'].value()
    if nuke.thisNode()['label'].evaluate():
        ll+= "\n"+ nuke.thisNode()['label'].evaluate()
    return ll

nuke.addAutolabel(TimeOffsetAutolabel, nodeClass= 'TimeOffset')

