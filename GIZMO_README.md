# Gizmo Loading System

This system automatically loads gizmo files from organized directory structures and adds them to the Nuke Nodes menu.

## How It Works

The `load_gizmos.py` script scans for `.gizmo` files in organized directory structures and automatically adds them to the Nuke menu system. It supports both the main `.nuke` directory and the `repos/nuketools` directory structure.

## Where to Place Gizmos

Place your gizmo files in one of these locations:

### 1. Main .nuke Directory
```
~/.nuke/groups/[Category]/[gizmo_name].gizmo
~/.nuke/groups/[Category]/[gizmo_name].png
```

### 2. NukeTools Repository
```
repos/nuketools/groups/[Category]/[gizmo_name].gizmo
repos/nuketools/groups/[Category]/[gizmo_name].png
```

## Directory Structure

Organize your gizmos by category in subdirectories:

```
groups/
├── Color/
│   ├── MyColorGizmo.gizmo
│   └── MyColorGizmo.png
├── Filter/
│   ├── MyFilterGizmo.gizmo
│   └── MyFilterGizmo.png
├── Transform/
│   ├── MyTransformGizmo.gizmo
│   └── MyTransformGizmo.png
└── Draw/
    ├── MyDrawGizmo.gizmo
    └── MyDrawGizmo.png
```

## Supported Categories

- **Color** - Color correction and grading tools
- **Filter** - Filtering and effects tools
- **Transform** - Transform and positioning tools
- **Draw** - Drawing and painting tools
- **Keyer** - Keying and matte tools
- **Time** - Time-based effects and retiming tools
- **3D** - 3D and geometry tools
- **Merge** - Compositing and merging tools
- **Views** - Viewer and display tools

You can create additional categories as needed.

## Icon Requirements

Each gizmo should have a corresponding icon file:
- **Primary format**: `.png` (recommended)
- **Alternative formats**: `.jpg`, `.jpeg`, `.tiff`, `.tif`
- **Naming**: Same name as the gizmo file (e.g., `MyGizmo.gizmo` → `MyGizmo.png`)
- **Size**: Recommended 32x32 pixels for best display

## Menu Structure

Gizmos will appear in the Nuke menu as:
- **With category**: `Nodes/SeanScripts/[Category]/[GizmoName]`
- **Without category**: `Nodes/SeanScripts/[GizmoName]`

## Configuration

The gizmo loading system can be configured by editing `gizmo_config.py`:

```python
# Log level for gizmo loading messages
# Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
# - DEBUG: Shows detailed information about each gizmo loaded
# - INFO: Shows summary information (default)
# - WARNING: Shows only warnings and errors
# - ERROR: Shows only errors
LOG_LEVEL = 'INFO'

# Whether to show statistics after loading
SHOW_STATS = True

# Whether to show placement guide when no gizmos are found
SHOW_PLACEMENT_GUIDE = True

# Custom directories to scan for gizmos
CUSTOM_GIZMO_DIRECTORIES = ['/path/to/custom/gizmos']

# Categories to include (leave empty for all categories)
INCLUDE_CATEGORIES = ['Color', 'Filter', 'Transform']

# Categories to exclude
EXCLUDE_CATEGORIES = ['Deprecated', 'Old']
```

## Usage

The gizmo loading system is automatically called when Nuke starts up. You can also run it manually:

```python
import load_gizmos

# Load gizmos with default settings
stats = load_gizmos.load_gizmos()

# Set log level to DEBUG for detailed information
load_gizmos.set_log_level('DEBUG')
stats = load_gizmos.load_gizmos()

# Print statistics
load_gizmos.print_loading_stats(stats)
```

## Troubleshooting

### No Gizmos Found
If no gizmos are loaded, check:
1. Gizmo files have `.gizmo` extension
2. Files are placed in the correct directory structure
3. Directory paths are correct

### Missing Icons
If gizmos load but show no icons:
1. Ensure icon files exist with the same name as the gizmo
2. Check icon file format (`.png` recommended)
3. Verify icon files are in the same directory as the gizmo

### Menu Conflicts
If you see duplicate menu items:
1. Check for duplicate gizmo files
2. Ensure gizmo names are unique within categories
3. Restart Nuke to clear any cached menu items

## Development

To add new gizmos:
1. Create your gizmo in Nuke
2. Save it as a `.gizmo` file
3. Create a corresponding icon file
4. Place both files in the appropriate category directory
5. Restart Nuke or reload the gizmo system

## Statistics

The system provides detailed statistics about the loading process:
- Total gizmos found
- Successfully loaded gizmos
- Missing icons
- Errors encountered
- Categories discovered

This helps diagnose any issues with the gizmo loading system. 