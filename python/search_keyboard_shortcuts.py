def search_keyboard_shortcuts():
    #Search keyboard shortcuts 
    #attempts to search for a given text in short cut keys
    #sean danischevsky 2014
    import nuke
    search= nuke.getInput    (     "Search hotkeys",    ""     )   
    result= ""
    keys= nuke.hotkeys().split("n")
    if not search:
        for key in keys: 
            result+= key+ "n"
    else:
        for key in keys: 
            if (search in key) or ('t' not in key):
                result+= key+ "n"
    return result


