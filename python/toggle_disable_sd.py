
import nuke

def toggleDisable(nodes):
    ##### Toggle Disable #####
    for node in nodes:
        try:
            node['disable'].setValue(not node['disable'].getValue())
        except NameError: 
            # no such knob
            pass
    return

if __name__ == '__main__':
    toggleDisable(nuke.selectedNodes())

