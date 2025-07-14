# Test script for load_test_image_sd
# Run this in Nuke's Script Editor to test the function

import load_test_image_sd

def test_load_test_image():
    """Test the load_test_image function"""
    print("Testing load_test_image function...")
    
    try:
        # Test loading the 2K version
        read_node_2k = load_test_image_sd.load_test_image()
        print(f"✓ Successfully loaded 2K test image: {read_node_2k['file'].value()}")
        
        # Test loading the 4K version
        read_node_4k = load_test_image_sd.load_test_image_4k()
        print(f"✓ Successfully loaded 4K test image: {read_node_4k['file'].value()}")
        
        print("✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Error: {e}")

# Run the test
if __name__ == "__main__":
    test_load_test_image() 