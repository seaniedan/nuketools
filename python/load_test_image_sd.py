# Load Test Image Function
# by Sean Danischevsky
#
# Loads the KODAK Digital LAD Test Image for testing and calibration purposes

import nuke
import os

def load_test_image():
    """
    Load the KODAK Digital LAD Test Image into a Read node.
    
    This function creates a Read node and sets it to load the LAD test image
    from the assets directory. The LAD (Laboratory Aim Density) test image
    is useful for color calibration and testing purposes.
    
    Returns:
        nuke.Node: The created Read node with the test image loaded
    """
    # Get the directory where this script is located
    this_dir = os.path.dirname(__file__)
    
    # Navigate up to the nuketools root directory and then to assets
    nuketools_root = os.path.dirname(this_dir)
    lad_image_path = os.path.join(nuketools_root, "assets", 
                                 "KODAK-Digital-LAD-Test-Image-DPX-Format", 
                                 "Digital_LAD_2048x1556.dpx")
    
    # Create a Read node
    read_node = nuke.createNode("Read")
    
    # Set the file path
    read_node["file"].setValue(lad_image_path)
    
    print(f"Loaded test image: {lad_image_path}")
    
    return read_node

def load_test_image_4k():
    """
    Load the 4K version of the KODAK Digital LAD Test Image.
    
    Returns:
        nuke.Node: The created Read node with the 4K test image loaded
    """
    # Get the directory where this script is located
    this_dir = os.path.dirname(__file__)
    
    # Navigate up to the nuketools root directory and then to assets
    nuketools_root = os.path.dirname(this_dir)
    lad_image_path = os.path.join(nuketools_root, "assets", 
                                 "KODAK-Digital-LAD-Test-Image-DPX-Format", 
                                 "Digital_LAD_4096x3112.dpx")
    
    # Create a Read node
    read_node = nuke.createNode("Read")
    
    # Set the file path
    read_node["file"].setValue(lad_image_path)
    
    print(f"Loaded 4K test image: {lad_image_path}")
    
    return read_node 