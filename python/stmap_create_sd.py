def stmap_create():
    import nuke
    #create blank ST map of the right size if we have a node selected
    #which can then be disconnected but retain the correct size
    #by Sean Danischevsky 2016

    #red
    rampr= nuke.createNode("Ramp")
    rampr['output'].enableChannel(1, 0) #g
    rampr['output'].enableChannel(2, 0) #b
    rampr['output'].enableChannel(3, 0) #a
    rampr['replace'].setValue(1)
    rampr['p0'].setValue([-0.5, 0])
    rampr['p1'].setValue([rampr.width()-.5, 0])

    #green
    rampg= nuke.createNode("Ramp")
    rampg['output'].enableChannel(0, 0) #r
    rampg['output'].enableChannel(2, 0) #b
    rampg['output'].enableChannel(3, 0) #a
    rampg['p0'].setValue([0, -0.5])
    rampg['p1'].setValue([0, rampg.height()-.5])
    rampg['replace'].setValue(1)
    rampg['output'].enableChannel(0, 0) 

    return

#runs when testing:
if __name__ == "__main__":
    stmap_create()