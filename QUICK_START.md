# NukeTools Quick Start Guide

Get up and running with NukeTools in minutes! This guide covers the essential setup and most commonly used features.

## 🚀 Installation

### Step 1: Clone the Repository
```bash
cd ~/.nuke
git clone https://github.com/seaniedan/nuketools.git
```

### Step 2: Add to Nuke
```bash
echo "nuke.pluginAddPath('nuketools')" >> init.py
```

### Step 3: Restart Nuke
You should now see:
- **SeanScripts** in the Nodes menu
- **SD** icon in the node panel
- **SDNukeTools** in the main menu

## 🎯 Essential Tools

### Node Organization
**Arrange By** - Organize nodes intelligently
- **Shortcut**: `Shift+L`
- **Use**: Select nodes → `Shift+L` → Choose criteria (class, position, etc.)

**Toggle Disable** - Quick enable/disable
- **Shortcut**: `Alt+Shift+d`
- **Use**: Select nodes → `Alt+Shift+d`

### File Management
**Recursive Read** - Load entire directories
- **Menu**: Nodes → Image → Recursive Read
- **Use**: Point to directory → Auto-creates Read nodes

**Copy Render Command** - Get command line render
- **Menu**: SDNukeTools → Python → Copy Command Line Render Command
- **Use**: Select Write nodes → Copy command to clipboard

### Script Cleanup
**Script Cleanup** - Optimize your script
- **Menu**: Edit → Script → Cleanup script
- **Use**: Removes errors, optimizes performance

## ⌨️ Essential Shortcuts

| Shortcut | Function | When to Use |
|----------|----------|-------------|
| `h` | Zoom to center | Lost in node graph |
| `Shift+L` | Arrange by... | Organizing nodes |
| `Alt+Shift+d` | Toggle disable | Testing changes |
| `Alt+d` | Make dot input | Connecting nodes |
| `Alt+c` | Copy paths | Sharing file locations |
| `Ctrl+k` | Shake clone | Creating variations |

## 🎬 Common Workflows

### 1. Setting Up a New Script
```python
# Load sequences
# Nodes → Image → Recursive Read → Select directory

# Organize nodes
# Select all → Shift+L → Arrange by class

# Clean up
# Edit → Script → Cleanup script
```

### 2. Render Management
```python
# Set up Write nodes
# Select Write nodes → SDNukeTools → Python → Copy Command Line Render Command

# Create directories
# Write nodes auto-create directories on render
```

### 3. Node Organization
```python
# Arrange by type
# Select nodes → Shift+L → Choose 'class'

# Create backdrops
# Select nodes → SDNukeTools → Backdrop → Scan Nodes for Backdrop collection
```

## 🔧 Quick Configuration

### Gizmo Settings (`gizmo_config.py`)
```python
# Show loading info
LOG_LEVEL = 'INFO'
SHOW_STATS = True

# Organize gizmos by category
INCLUDE_CATEGORIES = ['Color', 'Filter', 'Transform']
```

### Custom Gizmos
Place your gizmos in:
```
groups/
├── Color/          # Color correction tools
├── Filter/         # Filter effects
├── Transform/      # Transform tools
└── Draw/           # Drawing tools
```

## 🎨 Custom Viewers

Access via **Viewer** menu:
- **Flip/Flop** - Mirror operations
- **Grid** - Alignment overlay
- **Saturation** - Color analysis
- **Laplacian** - Edge detection

## 📁 File Operations

### Quick File Tasks
- **Copy paths**: `Alt+c` (select nodes)
- **Open directories**: `Shift+o` (select nodes)
- **Read from Write**: `Shift+R` (select Write nodes)

### Batch Operations
- **Convert to EXR**: SDNukeTools → Read → Split EXR channels
- **Collect files**: File → Collect Files
- **Sequence check**: SDNukeTools → Other → Analyse Input Sequences

## 🎯 Pro Tips

### 1. Node Movement
- **Translate**: `Shift + Arrow keys`
- **Scale**: `Shift+Alt + +/-`
- **Align**: `Alt + x/y`

### 2. Script Management
- **Auto-save**: Enabled by default
- **Font scaling**: `Ctrl + +/-`
- **Tidyness**: Edit → Script → Show Tidyness

### 3. 3D Tools
- **Smooth camera**: SDNukeTools → 3D → Smooth Selected Cameras
- **Snap to axis**: SDNukeTools → 3D → Animated Snap 3D

## 🆘 Troubleshooting

### Common Issues

**Gizmos not loading?**
- Check `gizmo_config.py` settings
- Verify directory structure
- Restart Nuke

**Menu items missing?**
- Check `init.py` configuration
- Verify Python script syntax
- Restart Nuke

**Performance issues?**
- Run script cleanup
- Organize nodes efficiently
- Remove unnecessary nodes

### Debug Mode
```python
# In gizmo_config.py
LOG_LEVEL = 'DEBUG'
```

## 📚 Next Steps

1. **Explore the menu system** - Browse SDNukeTools menu
2. **Try keyboard shortcuts** - Practice common operations
3. **Organize your gizmos** - Add custom tools to categories
4. **Read full documentation** - Check README.md and other docs

## 🎯 Essential Scripts to Know

### Node Management
- `arrange_by_sd.py` - Node arrangement
- `move_nodes_sd.py` - Node positioning
- `MassivePanel.py` - Bulk operations

### File Operations
- `recursive_read_sd.py` - Directory loading
- `copy_command_line_render_command_sd.py` - Render commands
- `collectFiles.py` - File collection

### Script Management
- `script_clean_sd.py` - Script optimization
- `backdrop_sd.py` - Backdrop management
- `autosave_sd.py` - Auto-saving

---

**Need help?** Check the main [README.md](README.md) or [Python Scripts Documentation](PYTHON_SCRIPTS_README.md) for detailed information.

*Happy compositing! 🎬* 