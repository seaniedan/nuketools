from .animatedSnap3D import *

import nuke
# Add menu items under the Axis Menu
try:
    m = nuke.menu('Axis').findItem('Snap')
    m.addSeparator()
    m.addCommand('Match animated position', 'animatedSnap3D.translateThisNodeToPointsAnimated()')
    m.addCommand('Match animated position, orientation', 'animatedSnap3D.translateRotateThisNodeToPointsAnimated()')
    m.addCommand('Match animated position, orientation, scale', 'animatedSnap3D.translateRotateScaleThisNodeToPointsAnimated()')
except:
    pass
