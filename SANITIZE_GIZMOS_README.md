# Sanitize Gizmos Tool

Converts `.gizmo` files to Group format with standardized naming, help text, and icon handling.

## Features

- **Unified Interface**: Single menu item handles files, directories, and selections
- **Smart Detection**: Automatically detects selected gizmo nodes in Nuke
- **Flexible Selection**: Choose single files, multiple files, or entire directories
- **File Browser Integration**: Select files/directories through Nuke's native file browser
- **Automatic Icon Copying**: Copies default icons from nuketools icons folder
- **Unified Configuration**: Uses `gizmo_config.py` for settings
- **Error Handling**: Comprehensive error reporting with summary
- **Batch Processing**: Process single files or entire directories recursively
- **Sanitization**: Converts Gizmo format to Group format with standardized naming

## Usage

### From Nuke Menu
**"SDNukeTools" > "Python" > "Sanitize Gizmos"** - Unified interface that handles:

1. **Selected Nodes**: If gizmo nodes are selected in Nuke, processes their files automatically
2. **File Selection**: Opens file dialog to select single or multiple `.gizmo` files
3. **Directory Selection**: Opens directory dialog to process all `.gizmo` files in a directory
4. **Mixed Selection**: Can handle combinations of files and directories

### Command Line
```bash
# Process single file
python repos/nuketools/python/sanitize_gizmos.py /path/to/file.gizmo

# Process directory
python repos/nuketools/python/sanitize_gizmos.py /path/to/gizmo/directory
```

### Programmatic
```python
import sanitize_gizmos

# Process single gizmo
success, message = sanitize_gizmos.sanitize_gizmo("/path/to/file.gizmo")

# Process directory
results = sanitize_gizmos.sanitize_directory("/path/to/directory")
```

## Configuration

The tool automatically finds the appropriate `gizmo_config.py` file based on where gizmos are being processed:

### Config Search Order
1. **Local Directory**: `gizmo_config.py` in the same directory as the gizmos
2. **Main .nuke Directory**: `~/.nuke/gizmo_config.py`
3. **Nuketools Directory**: `repos/nuketools/gizmo_config.py`
4. **Default Values**: Built-in defaults if no config found

### Config Structure
```python
GIZMO_CONVERSION = {
    "suffix": "_sd",                    # Suffix added to gizmo names
    "tile_color": "0xaaffffff",        # Tile color for converted groups
    "help": "Copyright Sean Danischevsky",  # Default help text
    "default_icon": "SeanScripts.png"   # Default icon to copy
}
```

### Example: Project-Specific Config
Place `gizmo_config.py` in your project's gizmo directory for project-specific settings:
```
project/
├── gizmos/
│   ├── gizmo_config.py          # Project-specific settings
│   ├── MyGizmo1.gizmo
│   └── MyGizmo2.gizmo
```

## What It Does

### File Conversion
- Converts `.gizmo` files from Gizmo to Group format
- Sanitizes filenames (ASCII only, valid characters)
- Adds standardized suffix (e.g., `_sd`)
- Converts internal "Gizmo" format to "Group" format

### Content Processing
- **Name Standardization**: Ensures consistent naming with suffix
- **Help Text**: Adds copyright and help information
- **Tile Color**: Sets consistent visual appearance
- **Position Cleanup**: Removes xpos, ypos, note_font data
- **Viewer Removal**: Removes Viewer sections from files

### Icon Handling
- Automatically copies default icon from nuketools icons folder
- Supports multiple formats (PNG, JPG, TIFF)
- Creates icon with sanitized filename

### Error Handling
- Comprehensive error reporting
- Continues processing on individual file errors
- Provides summary statistics
- Logs all operations with configurable verbosity

## Output

### Single File Processing
- Returns `(success: bool, message: str)`
- Success message includes output filename
- Error message includes specific failure reason

### Directory Processing
- Returns dictionary with statistics:
  ```python
  {
      "total": 10,           # Total gizmos found
      "success": 8,          # Successfully processed
      "errors": ["error1", "error2"],  # Error messages
      "processed": ["file1.gizmo", "file2.gizmo"]  # Success messages
  }
  ```

## File Structure

### Input
- `.gizmo` files (Nuke Gizmo format)
- Can be single files or directories

### Output
- `.gizmo` files (Nuke Group format)
- Icons copied to same directory as gizmo
- Original files moved/backed up based on settings

## Dependencies

- **Nuke**: For menu integration and file dialogs
- **Python Standard Library**: os, string, glob, shutil, logging, datetime
- **Configuration**: `gizmo_config.py` (automatically found based on gizmo location)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `sanitize_gizmos.py` is in the `repos/nuketools/python` directory
2. **Config Not Found**: Tool will use defaults if no `gizmo_config.py` found
3. **Icon Not Found**: Check that `SeanScripts.png` exists in nuketools icons
4. **Permission Errors**: Ensure write permissions to output directories
5. **Invalid Gizmo Format**: File must be valid Nuke Gizmo format

### Logging

The tool uses Python's logging module. Set `LOG_LEVEL` in config:
- `DEBUG`: Detailed processing information
- `INFO`: Standard operation messages (default)
- `WARNING`: Only warnings and errors
- `ERROR`: Only errors

### Error Recovery

- Failed files are logged but don't stop processing
- Original files are backed up before modification
- Use `rename_action="backup"` to preserve originals

## Examples

### Basic Usage
```python
# Convert single gizmo with default settings
success, message = sanitize_gizmos.sanitize_gizmo("my_gizmo.gizmo")

# Convert directory with custom settings
results = sanitize_gizmos.sanitize_directory(
    "/path/to/gizmos",
    suffix="_custom",
    tile_color="0xff0000ff",
    help="Custom Copyright 2024"
)
```

### Menu Integration
The tool automatically adds a menu item to the "SDNukeTools" > "Python" menu in Nuke:
- "Sanitize Gizmos" - Unified interface for all gizmo sanitization needs

## Version History

- **v2.2**: Unified interface - single function handles files, directories, and selections
- **v2.1**: Renamed functions and menu items to use "sanitize" terminology
- **v2.0**: Complete rewrite with menu integration, unified config, error handling
- **v1.0**: Original basic gizmo conversion functionality 