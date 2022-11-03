# Sean Danischevsky NukeTools init.py
#
# loaded by Foundry Nuke before menu.py

nuke.addFormat ('4096 4096 1.0 square_4K')

#some other formats you might enjoy:
#nuke.addFormat(6048 4032 2 Venice 6k 3x2 Anamorphic)
#nuke.addFormat(4096 3432 2 Venice 4k 6x5 Anamorphic)
#nuke.addFormat(4096 3024 2 Venice 4k 4x3 Anamorphic)
#nuke.addFormat(4096 1716 1 Venice 4k 239 Spherical)
#nuke.addFormat(6048 2534 1 Venice 6k 239 Spherical)
#nuke.addFormat(4096 2160 1 Panasonic SIH 4k Spherical)
#nuke.addFormat(5888 3312 1 Panasonic SIH 5k)
#nuke.addFormat(3840 2160 1 GoPro Hero UHD)
#nuke.addFormat(4096 2340 1 Phantom Flex 4k)
#nuke.addFormat(8192 4320 1 RED Monstro)
#nuke.addFormat(5760 3240 1 DJI Inspire 5.8k)
#nuke.addFormat(3840 2160 1 Sony 7)
#nuke.addFormat(4096 3024 1 Venice 4k 4x3 Spherical)
#nuke.addFormat(1920 1080 1 Panasonic SIH HD)
#nuke.addFormat(5280 2160 1 DJI Inspire 5.3k)
#nuke.addFormat(6016 3200 1 DJI Inspire 6k)
#nuke.addFormat(4000 3000 1 GoPro 4x3)
#nuke.addFormat(2160 3840 1 GoPro UHD Portrait)
#nuke.addFormat(1920 1080 1 GoPro HD)
#nuke.addFormat(1920 1440 1 GoPro 1920x1440)
#nuke.addFormat(4096 2160 1.3 Panasonic SIH 4k Anamorphic)    
#nuke.addFormat ('4096 3112 2.0 4K_Cinemascope(full-ap)')


#Nuke Viewers
#NoOp first, as if OCIO is removed, this will be the default viewer, rather than 'Flip':
nuke.ViewerProcess.register('No Operation', nuke.createNode,('NoOp', ))
nuke.ViewerProcess.register('Flip (mirror vertical)', nuke.createNode,('FlipViewer_sd', ))
nuke.ViewerProcess.register('Flop (mirror horizontal)', nuke.createNode,('FlopViewer_sd', ))
nuke.ViewerProcess.register('Grid', nuke.createNode,('GridViewer_sd', ))
nuke.ViewerProcess.register('Saturation', nuke.createNode,('Saturation_sd', ))
nuke.ViewerProcess.register('Laplacian', nuke.createNode,('LaplacianViewer_sd', ))
nuke.ViewerProcess.register('CheckFrozen', nuke.createNode,('CheckFrozenViewer_sd', ))
nuke.ViewerProcess.register('Corners', nuke.createNode,('ScrollViewer_sd', ))
