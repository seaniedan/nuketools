#tracker_median
#by Sean Danischevsky 2012

import nuke

def tracker_median_sd():
    #creates a tracker node with a median of all selected tracks in selected trackers!
    #by Sean Danischevsky 2012
    #average (maybe)
    #add 'throwaway outliers then recalculate mean' method

    def xy_median(xy_pairs):
        import math
        points= []
        for point in xy_pairs:
            points.append(math.hypot(point[0], point[1]))
        theValues= sorted(zip(points, xy_pairs))
        if len(theValues) %2== 1:
            return theValues[(len(theValues)+ 1)/ 2- 1][1]
        else:
            lower= theValues[len(theValues)/ 2- 1][1]
            upper= theValues[len(theValues)/ 2][1]
        return ((float(lower[0]+ upper[0]))/ 2,   (float(lower[1]+ upper[1])) / 2     )


    def throwaway_outliers(xy_pairs):
        #for now this really finds thecentre of (xy_pairs) 
        #in the future, will discard points 3 standard deviations from mean
        import math
        meanx= sum ([i[0] for i in xy_pairs])/ len(xy_pairs)
        meany= sum ([i[1] for i in xy_pairs])/ len(xy_pairs)
        points= []
        for point in xy_pairs:
            points.append(math.hypot(point[0]-meanx,point[1]-meany))
        theValues= list(zip(points,xy_pairs))
        median= min(theValues)
        print(median)
        return (median[1][0], median[1][1])


    def most_connected(xy_pairs):
        #return the most connected point, selected by distance from the origin
        #i.e. it finds the most 'clustered' point! :-))))
        import math
        points=[]
        for point in xy_pairs:
            dist= 0
            for pp in xy_pairs:
                dist+= math.hypot(point[0]-pp[0], point[1]-pp[1])
            points.append(dist)
        theValues= list(zip(points, xy_pairs))
        mostConnected= min(theValues)
        #should really check if there are several points equally connected, and average if so 
        return (mostConnected[1][0],mostConnected[1][1])


    #combine more than one tracker
    nodes= nuke.selectedNodes("Tracker3")
    #store all the tracks
    tracks= []
    for node in nodes:
        #check which tracks to use:
        if "T" in node['use_for1'].value():
            tracks.append(node['track1'])
        if "T" in node['use_for2'].value():
            tracks.append(node['track2'])
        if "T" in node['use_for3'].value():
            tracks.append(node['track3'])
        if "T" in node['use_for4'].value():
            tracks.append(node['track4'])
    #remove tracks that are not animated:
    for track in tracks:
        if track.isAnimated()== False:
            tracks.remove(track)
    #check we have at least 3, or there's no point doing a median! :-)
    if len(tracks)< 3:
        nuke.message("You need at least 3 tracks!\nSelect one or more Tracker nodes and check 'T' for each track you want to use.")
        return
    #find the first and last frames of animation
    #first:
    tracks[0].getKeyTime(0)
    first= min(track.getKeyTime(0) for track in tracks)
    #last
    last= max(track.getKeyTime(track.getNumKeys()) for track in tracks)

    #now find the median!!!!
    #get the xy *displacement* each frame. 
    xy= []#might not need this to store the result - go straight into tracker.
    for frame in range(int(first), int(last)+ 1):
        if not xy:
            #for the first point, use the average of tracks at first frame:
            #not mathematically necessary, but more user-friendly!
            avx= sum ([track.valueAt(first)[0] for track in tracks ])/len(tracks)
            avy= sum ([track.valueAt(first)[1] for track in tracks ])/len(tracks)
            xy.append((avx,avy))
        else:
            xyf= []
            for track in tracks:
                #Need to provide a list of track points: [[x,y],[x,y]] at each frame
                xyf.append((track.getValueAt(frame)[0]- track.getValueAt(frame- 1)[0], track.getValueAt(frame)[1]-track.getValueAt(frame- 1)[1]))

			#There is no definitive median for more than three points on a 2d plane.
			#Choose one of the different methods I have programmed:
			#TODO: could throwaway outlers until we have 3 points then do the 3 point median method.
            #medianDisplacement= most_connected(xyf)
            #medianDisplacement= throwaway_outliers(xyf)
            medianDisplacement= xy_median(xyf)
            
            #add median displacement to value of previous frame 
            newx= xy[-1][0]+ medianDisplacement[0]
            newy= xy[-1][1]+ medianDisplacement[1]
            xy.append((newx, newy))

    #print xy
    #make the tracker
    tracker= nuke.createNode("Tracker3")
    tracker['transform'].setValue("stabilize")
    #tracker['reference_frame'].setValue(int(first))
    tracker['track1'].setAnimated()
    #set the points
    count= 0
    for frame in range(int(first), int(last)+ 1):
        #set x
        tracker['track1'].setValueAt( xy[count][0], frame, 0 )
        #set y
        tracker['track1'].setValueAt( xy[count][1], frame, 1 )
        count+= 1
    return


###########################
#runs when testing:
if __name__ == "__main__":
    tracker_median_sd()

