# NukeTools

A comprehensive collection of tools, scripts, and gizmos for Foundry Nuke, designed to enhance workflow efficiency and provide powerful automation capabilities for visual effects and compositing artists.

## Overview

NukeTools is a curated collection of Python scripts, custom gizmos, and utilities that extend Nuke's functionality with features like:
- Automated gizmo management and loading
- Node organization and arrangement tools
- File management and batch processing
- Script cleanup and optimization
- Custom viewer processes
- 3D and camera tools
- And much more

## Quick Installation

### Linux/macOS
```bash
cd ~/.nuke
git clone https://github.com/seaniedan/nuketools.git
echo "nuke.pluginAddPath('nuketools')" >> init.py
```

### Windows
```cmd
cd %USERPROFILE%\.nuke
git clone https://github.com/seaniedan/nuketools.git
echo nuke.pluginAddPath('nuketools') >> init.py
```

### Verification
After installation and restarting Nuke, you should see:
- An **SD** icon in the node panel
- A **SDNukeTools** menu in the main Nuke menu

## Features

### 🎯 Core Tools

#### Gizmo Management
- **Automatic Gizmo Loading**: Automatically loads and organizes gizmos from categorized directories
- **Gizmo Sanitization**: Converts and standardizes gizmo files with consistent naming and metadata
- **Icon Management**: Automatic icon copying and organization

#### Node Organization
- **Arrange By**: Intelligent node arrangement based on various criteria (position, class, metadata, etc.)
- **MassivePanel**: Advanced panel for bulk node operations and property management
- **Node Movement**: Precise node positioning, scaling, and rotation tools
- **Backdrop Management**: Automatic backdrop creation and organization

#### Script Management
- **Script Cleanup**: Comprehensive script optimization and cleanup tools
- **Tidyness Analysis**: Analyze and improve script organization
- **Search & Replace**: Advanced search and replace functionality for node properties

### 📁 File Management

#### File Operations
- **Recursive Read**: Automatically create Read nodes for entire directory structures
- **Collect Files**: Gather and organize project files
- **Copy Commands**: Copy file paths, render commands, and frame ranges to clipboard
- **File Conversion**: Convert between various file formats

#### Render Management
- **Render Range Tools**: Manage render ranges and frame lists
- **Command Line Render**: Generate command-line render commands
- **Write Directory Creation**: Automatic directory creation for Write nodes

### 🎬 Viewer & Display

#### Custom Viewers
- **Flip/Flop Viewers**: Mirror operations for viewer
- **Grid Viewer**: Grid overlay for alignment
- **Saturation Viewer**: Saturation analysis
- **Laplacian Viewer**: Edge detection visualization
- **CheckFrozen Viewer**: Frozen frame detection
- **Scroll Viewer**: Corner pin visualization

#### Display Tools
- **Screengrab**: Capture viewer screenshots
- **Thumbnails**: Generate node thumbnails
- **Viewer Handles**: Set viewer handle ranges

### 🔧 Utility Tools

#### 3D & Camera
- **Animated Snap 3D**: Snap 3D objects to axes
- **Smooth Camera**: Create smooth camera animations
- **Camera from Metadata**: Generate cameras from metadata
- **CornerPin Conversion**: Convert between CornerPin types

#### Animation & Tracking
- **Tracker Median**: Pick best tracking data
- **Animation Curves**: Copy animation curves between nodes
- **Tween Nodes**: Interpolate between node positions
- **Shake Style Clone**: One-way cloning system

#### Automation
- **Autosave**: Automatic script saving
- **Autolabel**: Automatic node labeling
- **Node Defaults**: Set default node properties
- **Font Size Adjustment**: Dynamic font scaling

## Directory Structure

```
nuketools/
├── init.py                 # Nuke initialization script
├── menu.py                 # Menu creation and organization
├── gizmo_config.py         # Gizmo loading configuration
├── python/                 # Python scripts and tools
│   ├── load_gizmos.py      # Gizmo loading system
│   ├── sanitize_gizmos.py  # Gizmo sanitization tool
│   ├── arrange_by_sd.py    # Node arrangement tool
│   ├── MassivePanel.py     # Bulk operations panel
│   ├── script_clean_sd.py  # Script cleanup utilities
│   └── ...                 # Additional tools
├── groups/                 # Custom gizmos organized by category
│   ├── Color/              # Color correction gizmos
│   ├── Filter/             # Filter and effects gizmos
│   ├── Transform/          # Transform gizmos
│   ├── Draw/               # Drawing gizmos
│   ├── Keyer/              # Keying gizmos
│   ├── Time/               # Time-based effects
│   ├── Merge/              # Compositing gizmos
│   └── Views/              # Viewer gizmos
├── gizmos/                 # Additional gizmo files
├── icons/                  # Icon files for gizmos
└── README files            # Detailed documentation
```

## Menu Organization

### Main Nuke Menu
- **File**: Nuke/NukeX switching, file collection
- **Edit**: Node operations, arrangement, cleanup
- **Viewer**: Handle management, custom viewers
- **SDNukeTools**: Comprehensive tool collection

### Nodes Menu
- **SeanScripts**: Organized gizmo categories
- **Image**: Recursive read, read from write
- **Transform**: Various transform utilities

## Configuration

### Gizmo Configuration (`gizmo_config.py`)
```python
# Log level for gizmo loading
LOG_LEVEL = 'INFO'

# Show statistics after loading
SHOW_STATS = True

# Custom gizmo directories
CUSTOM_GIZMO_DIRECTORIES = []

# Categories to include/exclude
INCLUDE_CATEGORIES = []
EXCLUDE_CATEGORIES = []

# Gizmo conversion settings
GIZMO_CONVERSION = {
    "suffix": "_sd",
    "tile_color": "0xaaffffff",
    "help": "Copyright Sean Danischevsky",
    "default_icon": "SeanScripts.png"
}
```

## Usage Examples

### Basic Node Arrangement
```python
# Arrange selected nodes by class
import arrange_by_sd
arrange_by_sd.arrange_by(nuke.selectedNodes(), sortKey='class')
```

### Gizmo Sanitization
```python
# Sanitize a gizmo file
import sanitize_gizmos
success, message = sanitize_gizmos.sanitize_gizmo("/path/to/gizmo.gizmo")
```

### Script Cleanup
```python
# Clean up entire script
import script_clean_sd
script_clean_sd.cleanupScript(nuke.allNodes())
```

## Keyboard Shortcuts

| Shortcut | Function | Context |
|----------|----------|---------|
| `h` | Zoom to center | DAG |
| `Alt+Shift+d` | Toggle disable | DAG |
| `Shift+L` | Arrange by... | DAG |
| `Alt+d` | Make dot input | DAG |
| `Alt+c` | Copy paths to clipboard | DAG |
| `Shift+o` | Open directories in browser | DAG |
| `Ctrl+k` | Shake style clone | DAG |
| `Alt+v` | Paste multiple | DAG |

## Troubleshooting

### Common Issues

1. **Gizmos not loading**
   - Check file permissions
   - Verify directory structure
   - Check `gizmo_config.py` settings

2. **Menu items missing**
   - Restart Nuke after installation
   - Check `init.py` path configuration
   - Verify Python script syntax

3. **Import errors**
   - Ensure all dependencies are available
   - Check Python version compatibility
   - Verify file paths

### Debug Mode
Enable debug logging in `gizmo_config.py`:
```python
LOG_LEVEL = 'DEBUG'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your tools to appropriate directories
4. Update documentation
5. Submit a pull request

## Documentation

- [Gizmo Loading System](GIZMO_README.md) - Detailed gizmo management documentation
- [Sanitize Gizmos Tool](SANITIZE_GIZMOS_README.md) - Gizmo conversion and standardization
- [Python Scripts](python/) - Individual script documentation

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Author

**Sean Danischevsky** - [GitHub](https://github.com/seaniedan)

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check existing documentation
- Review the troubleshooting section

---

*NukeTools is designed to enhance your Nuke workflow with powerful automation and organization tools. Happy compositing!*
