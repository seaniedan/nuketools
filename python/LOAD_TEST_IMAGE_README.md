# Load Test Image Function

This module provides functions to load KODAK Digital LAD (Laboratory Aim Density) test images into Nuke for color calibration and testing purposes.

## Functions

### `load_test_image()`
Loads the 2K version (2048x1556) of the KODAK Digital LAD Test Image.

**Returns:** A Read node with the test image loaded

### `load_test_image_4k()`
Loads the 4K version (4096x3112) of the KODAK Digital LAD Test Image.

**Returns:** A Read node with the test image loaded

## Usage

### From Menu
The functions are available in the Nuke menu under:
- **Nodes > Draw > Load Test Image > LAD Test Image (2K)**
- **Nodes > Draw > Load Test Image > LAD Test Image (4K)**

### From Python Script
```python
import load_test_image_sd

# Load 2K test image
read_node = load_test_image_sd.load_test_image()

# Load 4K test image
read_node_4k = load_test_image_sd.load_test_image_4k()
```

### From Render Scripts
Since render scripts don't load menu.py, you can import and use the function directly:
```python
import load_test_image_sd
read_node = load_test_image_sd.load_test_image()
```

## Test Image Location
The test images are located in the nuketools repository at:
- `assets/KODAK-Digital-LAD-Test-Image-DPX-Format/Digital_LAD_2048x1556.dpx` (2K)
- `assets/KODAK-Digital-LAD-Test-Image-DPX-Format/Digital_LAD_4096x3112.dpx` (4K)

## Testing
Run the test script to verify the function works:
```python
import test_load_test_image
test_load_test_image.test_load_test_image()
```

## Notes
- The LAD test image is useful for color calibration and testing color pipelines
- The function automatically positions the Read node at (0,0) in the DAG
- Both functions return the created Read node for further manipulation if needed 