# Python Scripts Documentation

This document provides detailed information about all Python scripts included in the NukeTools repository, organized by functionality and category.

## Table of Contents

- [Node Management](#node-management)
- [File Operations](#file-operations)
- [Script Management](#script-management)
- [Viewer & Display](#viewer--display)
- [3D & Camera Tools](#3d--camera-tools)
- [Animation & Tracking](#animation--tracking)
- [Utility Tools](#utility-tools)
- [Configuration & Setup](#configuration--setup)

---

## Node Management

### Core Node Tools

#### `arrange_by_sd.py`
**Purpose**: Intelligent node arrangement based on various criteria
**Usage**: Arrange nodes by class, position, metadata, or custom properties
```python
import arrange_by_sd
# Arrange by class
arrange_by_sd.arrange_by(nuke.selectedNodes(), sortKey='class')
# Arrange by position
arrange_by_sd.arrange_by(nuke.selectedNodes(), sortKey='xpos', sortArrange='horizontal')
```

#### `move_nodes_sd.py`
**Purpose**: Precise node positioning, scaling, and rotation
**Features**:
- Translate nodes in any direction
- Scale nodes uniformly or per-axis
- Rotate nodes clockwise/counterclockwise
- Align nodes to grid or other nodes

```python
import move_nodes_sd
# Move nodes left
move_nodes_sd.translate_nodes_left(nuke.selectedNodes())
# Scale nodes up
move_nodes_sd.scale_nodes(nuke.selectedNodes(), 1.1, 1.1)
```

#### `MassivePanel.py`
**Purpose**: Advanced panel for bulk node operations
**Features**:
- Mass property changes across multiple nodes
- Search and replace functionality
- Animation control
- Node selection management

**Access**: `SDNukeTools > Python > MassivePanel`

#### `toggle_disable_sd.py`
**Purpose**: Toggle disable state of selected nodes
**Shortcut**: `Alt+Shift+d` (DAG context)

#### `make_dot_input_sd.py`
**Purpose**: Create dot inputs for selected nodes
**Shortcut**: `Alt+d` (DAG context)

### Node Information

#### `multiple_node_info_sd.py`
**Purpose**: Display detailed information about multiple nodes
**Features**:
- File information
- Metadata analysis
- Property comparison
- Batch reporting

#### `autolabel_sd.py`
**Purpose**: Automatic node labeling based on properties
**Features**:
- Smart label generation
- Custom label templates
- Batch labeling

---

## File Operations

### File Management

#### `recursive_read_sd.py`
**Purpose**: Automatically create Read nodes for entire directory structures
**Features**:
- Recursive directory scanning
- Multiple file format support
- Filtering options
- Batch processing

```python
import recursive_read_sd
# Read all EXR files in directory
recursive_read_sd.recursive_read(
    walkPaths='/path/to/directory',
    extRead=['.exr', '.dpx'],
    latest=True
)
```

#### `collectFiles.py`
**Purpose**: Gather and organize project files
**Features**:
- File collection from script
- Directory organization
- Format conversion
- Project archiving

#### `copy_file_to_clipboard_sd.py`
**Purpose**: Copy file paths and information to clipboard
**Features**:
- Copy file paths
- Open directories in browser
- Copy metadata
- Batch operations

**Shortcuts**:
- `Alt+c`: Copy paths to clipboard
- `Shift+o`: Open directories in browser

#### `read_from_write_sd.py`
**Purpose**: Create Read nodes from Write nodes
**Shortcut**: `Shift+R` (DAG context)

### Render Management

#### `copy_command_line_render_command_sd.py`
**Purpose**: Generate command-line render commands
**Features**:
- Copy render commands to clipboard
- Support for Write and WriteTank nodes
- Frame range inclusion
- Executable path detection

#### `render_range_sd.py`
**Purpose**: Manage render ranges and frame lists
**Features**:
- Frame range calculation
- Render list generation
- Batch processing

#### `render_one_after_the_other_sd.py`
**Purpose**: Sequential rendering of multiple nodes
**Features**:
- Queue management
- Error handling
- Progress tracking

#### `make_write_directories_sd.py`
**Purpose**: Automatic directory creation for Write nodes
**Features**:
- Pre-render directory creation
- Support for multiple node types
- Error handling

#### `copy_write_range_sd.py`
**Purpose**: Copy Write node frame ranges
**Features**:
- Range extraction
- Clipboard integration
- Batch operations

#### `copy_frame_list_to_clipboard_sd.py`
**Purpose**: Copy frame lists to clipboard
**Features**:
- Frame list generation
- Multiple formats
- Custom ranges

### File Conversion

#### `convert_to_exr_sd.py`
**Purpose**: Convert files to EXR format
**Features**:
- Batch conversion
- Quality preservation
- Metadata handling

#### `split_to_frames_sd.py`
**Purpose**: Split sequences into individual frames
**Features**:
- Frame extraction
- Format preservation
- Batch processing

---

## Script Management

### Script Cleanup

#### `script_clean_sd.py`
**Purpose**: Comprehensive script optimization and cleanup
**Features**:
- Node cleanup
- Error removal
- Optimization
- Organization

```python
import script_clean_sd
# Clean entire script
script_clean_sd.cleanupScript(nuke.allNodes())
# Delete errored nodes
script_clean_sd.delete_all_errored_nodes(nuke.selectedNodes())
```

#### `tidyness_sd.py`
**Purpose**: Analyze and improve script organization
**Features**:
- Tidyness scoring
- Layout analysis
- Optimization suggestions

#### `fix_nuke_script.py`
**Purpose**: Fix common Nuke script issues
**Features**:
- Error correction
- Compatibility fixes
- Performance optimization

### Search & Replace

#### `SearchReplacePanel.py`
**Purpose**: Advanced search and replace functionality
**Features**:
- Property search
- Batch replacement
- History management
- Pattern matching

**Access**: `SDNukeTools > Python > SearchReplacePanel`

### Backdrop Management

#### `backdrop_sd.py`
**Purpose**: Automatic backdrop creation and management
**Features**:
- Auto-coloring based on text
- Node collection
- Organization tools
- Smart grouping

---

## Viewer & Display

### Custom Viewers

#### `screengrab_viewer_sd.py`
**Purpose**: Capture viewer screenshots
**Features**:
- High-quality captures
- Multiple formats
- Batch processing

#### `thumbnails_sd.py`
**Purpose**: Generate node thumbnails
**Features**:
- Thumbnail generation
- Batch processing
- Format options

#### `set_viewer_handles.py`
**Purpose**: Set viewer handle ranges
**Features**:
- Handle management
- Preset ranges
- Custom ranges

### Display Tools

#### `write_name_in_dag_sd.py`
**Purpose**: Create messages or images in the node graph
**Features**:
- Text display
- Image insertion
- Custom positioning

---

## 3D & Camera Tools

### 3D Operations

#### `animatedSnap3D/`
**Purpose**: Snap 3D objects to axes
**Features**:
- Axis snapping
- Animation support
- Precision control

#### `create_smooth_camera.py`
**Purpose**: Create smooth camera animations
**Features**:
- Path smoothing
- Keyframe optimization
- Animation curves

#### `create_camera_from_metadata_sd.py`
**Purpose**: Generate cameras from metadata
**Features**:
- Metadata extraction
- Camera creation
- Parameter mapping

### Transform Tools

#### `convert_CornerPin_to_Smart_CornerPin_sd.py`
**Purpose**: Convert between CornerPin types
**Features**:
- Format conversion
- Parameter mapping
- Mocha tracker support

#### `uncrop_sd.py`
**Purpose**: Remove crop operations
**Features**:
- Crop reversal
- Parameter calculation
- Node replacement

---

## Animation & Tracking

### Tracking Tools

#### `tracker_median_sd.py`
**Purpose**: Pick best tracking data
**Features**:
- Track analysis
- Quality assessment
- Data selection

#### `copy_animation_curves_on_this_frame_sd.py`
**Purpose**: Copy animation curves between nodes
**Features**:
- Curve copying
- Frame-specific operations
- Parameter mapping

### Animation Tools

#### `tween_nodes_sd.py`
**Purpose**: Interpolate between node positions
**Features**:
- Position interpolation
- Keyframe generation
- Smooth transitions

#### `shake_style_clone.py`
**Purpose**: One-way cloning system
**Features**:
- Shake-style cloning
- Parameter linking
- Update management

**Shortcut**: `Ctrl+k` (DAG context)

---

## Utility Tools

### Automation

#### `autosave_sd.py`
**Purpose**: Automatic script saving
**Features**:
- Auto-save on changes
- Backup management
- Version control

#### `node_defaults.py`
**Purpose**: Set default node properties
**Features**:
- Property defaults
- Node templates
- Batch configuration

#### `adjust_font_sizes_sd.py`
**Purpose**: Dynamic font scaling
**Features**:
- Font size adjustment
- UI scaling
- Accessibility

**Shortcuts**:
- `Ctrl+=`: Increase font size
- `Ctrl+-`: Decrease font size

### Clipboard Operations

#### `copy_instead_of_render_sd.py`
**Purpose**: Copy operations instead of rendering
**Features**:
- Operation copying
- Performance optimization
- Workflow enhancement

#### `copy_rotopaint_range_sd.py`
**Purpose**: Copy Rotopaint ranges
**Features**:
- Range extraction
- Clipboard integration
- Batch operations

### Selection & Organization

#### `select_left_to_right_sd.py`
**Purpose**: Sort selection order from left to right
**Features**:
- Selection ordering
- Spatial organization
- Workflow optimization

#### `paste_multiple_sd.py`
**Purpose**: Paste multiple nodes
**Features**:
- Batch pasting
- Position management
- Organization

**Shortcut**: `Alt+v` (DAG context)

### Information & Debugging

#### `print_environment_variables_sd.py`
**Purpose**: Print environment variables
**Features**:
- Environment inspection
- Debug information
- System analysis

#### `print_nuke_paths_sd.py`
**Purpose**: Print Nuke paths
**Features**:
- Path inspection
- Configuration analysis
- Debug information

#### `print_python_modules_sd.py`
**Purpose**: Print Python modules
**Features**:
- Module inspection
- Dependency analysis
- Debug information

#### `search_keyboard_shortcuts.py`
**Purpose**: Search keyboard shortcuts
**Features**:
- Shortcut discovery
- Key mapping
- Documentation

### Sequence Management

#### `sequence_check_sd.py`
**Purpose**: Check sequence integrity
**Features**:
- Frame analysis
- Missing frame detection
- Sequence validation

#### `set_frame_range_to_selected_sd.py`
**Purpose**: Set frame range to selected nodes
**Features**:
- Range calculation
- Node analysis
- Automatic setting

### Stitching & Merging

#### `stitch_sd.py`
**Purpose**: Stitch operations
**Features**:
- Image stitching
- Seam detection
- Quality optimization

#### `stmap_create_sd.py`
**Purpose**: Create STMap nodes
**Features**:
- Map generation
- Distortion handling
- Workflow optimization

### Upstream Analysis

#### `upstream_sd.py`
**Purpose**: Analyze upstream nodes
**Features**:
- Dependency analysis
- Node tracing
- Workflow optimization

---

## Configuration & Setup

### Core Configuration

#### `gizmo_config.py`
**Purpose**: Gizmo loading configuration
**Features**:
- Loading settings
- Category management
- Logging configuration
- Custom directories

#### `load_gizmos.py`
**Purpose**: Gizmo loading system
**Features**:
- Automatic loading
- Category organization
- Icon management
- Error handling

#### `sanitize_gizmos.py`
**Purpose**: Gizmo sanitization and conversion
**Features**:
- Format conversion
- Name standardization
- Metadata management
- Icon handling

### Launch & Environment

#### `launch_nukeX.py`
**Purpose**: Switch between Nuke and NukeX
**Features**:
- License management
- Application switching
- Script preservation

**Menu**: File > Jump to NukeX / Jump to regular Nuke

#### `zoom_to_1_sd.py`
**Purpose**: Zoom to center of Nuke DAG
**Shortcut**: `h` (DAG context)

---

## Usage Patterns

### Common Workflows

1. **Script Organization**
   ```python
   # Clean and organize script
   import script_clean_sd
   script_clean_sd.cleanupScript(nuke.allNodes())
   
   # Arrange nodes by class
   import arrange_by_sd
   arrange_by_sd.arrange_by(nuke.selectedNodes(), sortKey='class')
   ```

2. **File Management**
   ```python
   # Create Read nodes for directory
   import recursive_read_sd
   recursive_read_sd.recursive_read('/path/to/sequences')
   
   # Copy render command
   import copy_command_line_render_command_sd
   copy_command_line_render_command_sd.copy_command_line_render_command_to_clipboard()
   ```

3. **Node Operations**
   ```python
   # Move nodes
   import move_nodes_sd
   move_nodes_sd.translate_nodes_right(nuke.selectedNodes())
   
   # Toggle disable
   import toggle_disable_sd
   toggle_disable_sd.toggleDisable(nuke.selectedNodes())
   ```

### Best Practices

1. **Always backup scripts before major operations**
2. **Use keyboard shortcuts for common operations**
3. **Organize gizmos in appropriate categories**
4. **Regular script cleanup for performance**
5. **Test tools on non-critical scripts first**

---

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check Python version compatibility
   - Verify file paths
   - Ensure dependencies are available

2. **Menu Items Missing**
   - Restart Nuke after installation
   - Check `init.py` configuration
   - Verify script syntax

3. **Performance Issues**
   - Use script cleanup tools
   - Organize nodes efficiently
   - Remove unnecessary nodes

### Debug Mode

Enable debug logging in `gizmo_config.py`:
```python
LOG_LEVEL = 'DEBUG'
```

---

## Contributing

When adding new scripts:

1. Follow the naming convention: `script_name_sd.py`
2. Include comprehensive docstrings
3. Add appropriate menu integration
4. Update this documentation
5. Test thoroughly before submission

---

*For detailed information about specific tools, refer to the individual script files and their docstrings.* 