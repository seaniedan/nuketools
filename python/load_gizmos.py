# automatically add gizmos to folders in which they are placed 
# by Sean Danischevsky 2022

# if no node_menu is given, the gizmos will appear mixed eith Nuke's regular nodes.
# if no directory is given, assumes the gizmos directory underneath menu.py.

import nuke, os

def load_gizmos(node_menu=nuke.menu('Nodes'), dir_of_gizmo_dirs=os.path.abspath( os.path.join (os.path.dirname(__file__), '../groups'))):

    for root, dirs, files in os.walk(dir_of_gizmo_dirs):
        for file in files:
            gizmo_name, ext = os.path.splitext(os.path.basename(file))
            if ext == ".gizmo":
                _, submenu_name = root.split(dir_of_gizmo_dirs)
                submenu_name = submenu_name.strip("/")
                if submenu_name:
                    node_menu.addCommand(f"{submenu_name}/{gizmo_name}", f"nuke.createNode('{gizmo_name}')", icon=f'{os.path.join(root, gizmo_name)}.png')
                else:
                    print (gizmo_name)
                    node_menu.addCommand(f"{gizmo_name}/{gizmo_name}", f"nuke.createNode('{gizmo_name}')", icon=f'{os.path.join(root, gizmo_name)}.png')
                nuke.pluginAddPath(os.path.join(root, *dirs))

if __name__ == '__main__':
    load_gizmos()



