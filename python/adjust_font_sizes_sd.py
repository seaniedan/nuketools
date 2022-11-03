

def adjust_font_sizes(adjust= 1):
    import nuke
    #=======================================
    #CTRL + plus/minus to change font size for all panes
    #by Sean Danischevsky 2014
    #would be nice to get it to work only on focus pane
    #e.g. only affect 'script editor' if in that pane
    #You can change relative font sizes in preferences 
    #to always make particular fonts bigger or smaller

    def adjust_font_size(font):
        prefs= nuke.toNode("preferences")
        val= prefs[font].getValue() or prefs['UIFontSize'].value() or 14#hack for 10.0+ nuke as scripteditorsize is broken
        val+= adjust
        if val>= 5 and val<= 100:
            prefs[font].setValue(val)
            print((font, prefs[font].value()))
        else:
            print((font, "limit reached!"))
        return 

    for font in ['ScriptEditorFontSize', 'UIFontSize', 'LabelSize']:
        adjust_font_size(font)
