#!/usr/bin/env python3
"""
Gizmo Sanitization and Conversion Tool

This tool converts .gizmo files to .gizmo Group format with standardized naming,
help text, and icon handling. It can process single files or entire directories.

Features:
- Menu integration with file/directory browser dialogs
- Automatic icon copying from nuketools icons folder
- Unified configuration system
- Error handling with summary reporting
- Sanitizes names, adds help text, removes position data
- Converts Gizmo format to Group format

Usage:
- Run from Nuke menu: "Sean" > "Save Gizmo" or "Sean" > "Save Gizmo Directory"
- Or call functions directly: sanitize_gizmo() or sanitize_directory()
"""

import os
import string
import glob
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config_for_directory(directory_path):
    """
    Load gizmo config from the appropriate location based on directory.
    
    Args:
        directory_path: Path to the directory containing gizmos
    
    Returns:
        dict: Configuration dictionary
    """
    import sys
    
    # Default config
    default_config = {
        "suffix": "_sd",
        "tile_color": "0xaaffffff", 
        "help": "Copyright Sean Danischevsky",
        "default_icon": "SeanScripts.png"
    }
    
    # Try to find config file in the same directory as the gizmos
    if directory_path:
        config_path = os.path.join(directory_path, "gizmo_config.py")
        if os.path.exists(config_path):
            try:
                # Add directory to path temporarily
                sys.path.insert(0, directory_path)
                import gizmo_config
                if hasattr(gizmo_config, 'GIZMO_CONVERSION'):
                    logger.info(f"Loaded config from: {config_path}")
                    return gizmo_config.GIZMO_CONVERSION
            except ImportError:
                pass
            finally:
                # Remove from path
                if directory_path in sys.path:
                    sys.path.remove(directory_path)
    
    # Try to load from main .nuke directory
    try:
        from gizmo_config import GIZMO_CONVERSION
        logger.info("Loaded config from main .nuke directory")
        return GIZMO_CONVERSION
    except ImportError:
        pass
    
    # Try to load from nuketools directory
    try:
        nuketools_config_path = os.path.join(os.path.dirname(__file__), "..", "gizmo_config.py")
        if os.path.exists(nuketools_config_path):
            sys.path.insert(0, os.path.dirname(nuketools_config_path))
            import gizmo_config
            if hasattr(gizmo_config, 'GIZMO_CONVERSION'):
                logger.info(f"Loaded config from: {nuketools_config_path}")
                return gizmo_config.GIZMO_CONVERSION
    except ImportError:
        pass
    
    logger.info("Using default config")
    return default_config

# Global config - will be set when processing starts
CONFIG = None

# Default nuketools icons path
NUKETOOLS_ICONS = os.path.join(os.path.dirname(__file__), "..", "icons")


def get_year():
    """Get current year for copyright notices."""
    return datetime.now().year


def read_file(filepath):
    """Read file and return lines as list."""
    try:
        with open(filepath, 'r') as fp:
            return fp.readlines()
    except Exception as e:
        logger.error(f"Failed to read {filepath}: {e}")
        return None


def write_file(filepath, lines):
    """Write lines to file."""
    try:
        with open(filepath, 'w') as fp:
            for line in lines:
                fp.write(line)
        return True
    except Exception as e:
        logger.error(f"Failed to write {filepath}: {e}")
        return False


def sanitise_gizmo_name(potential_gizmo_name, suffix):
    """Sanitize gizmo name to valid filename format."""
    # Only ASCII characters
    valid_filename = potential_gizmo_name.encode('ascii', 'ignore').decode('ascii')

    # Only valid characters
    valid_chars = f"{string.ascii_letters}{string.digits} _"
    valid_filename = "".join(character for character in valid_filename if character in valid_chars)

    # At least one letter
    valid_chars = f"{string.ascii_letters}"
    test_filename = "".join(character for character in potential_gizmo_name if character in valid_chars)
    if len(test_filename) == 0:
        valid_filename = "Group"
    
    # Capitalize first letter
    current_gizmo_name = valid_filename[0].upper() + valid_filename[1:]

    # Add suffix if not present
    if current_gizmo_name.endswith(suffix):
        sanitized_gizmo_name = current_gizmo_name
    else:        
        sanitized_gizmo_name = current_gizmo_name + suffix

    return sanitized_gizmo_name


def copy_default_icon(gizmo_name, target_dir, config=None):
    """Copy default icon from nuketools to target directory."""
    if config is None:
        config = CONFIG or {}
        
    if not os.path.exists(NUKETOOLS_ICONS):
        logger.warning(f"Nuketools icons directory not found: {NUKETOOLS_ICONS}")
        return False
    
    default_icon = config.get("default_icon", "SeanScripts.png")
    source_icon = os.path.join(NUKETOOLS_ICONS, default_icon)
    
    if not os.path.exists(source_icon):
        logger.warning(f"Default icon not found: {source_icon}")
        return False
    
    # Try different icon formats
    icon_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.tif']
    base_name = sanitise_gizmo_name(gizmo_name, config.get("suffix", "_sd"))
    
    for fmt in icon_formats:
        target_icon = os.path.join(target_dir, f"{base_name}{fmt}")
        try:
            shutil.copy2(source_icon, target_icon)
            logger.info(f"Copied default icon: {target_icon}")
            return True
        except Exception as e:
            logger.debug(f"Failed to copy icon with format {fmt}: {e}")
    
    return False


def edit_gizmo_file(lines, gizmo_name, tile_color=None, help=None):
    """Edit gizmo file content to convert to Group format."""
    import re

    if not lines:
        raise ValueError("No content to edit")

    # Replace Gizmo with Group
    for i, line in enumerate(lines):
        if line.startswith('Gizmo {'):
            lines[i] = 'Group {\n'
            logger.info("Replaced Gizmo with Group")

    # Find group section
    group_start = None
    for n, line in enumerate(lines):
        if line.startswith('Group {') or line.startswith('Gizmo {'):
            group_start = n
            break
    
    if group_start is None:
        raise ValueError('Not a valid Group/Gizmo file!')

    group_lines = lines[group_start:]
    
    # Find group end
    try:
        group_end_line = group_lines.index('}\n') + 1
    except ValueError:
        raise ValueError('Invalid Group structure - missing closing brace')

    group_lines, remaining_lines = group_lines[:group_end_line], group_lines[group_end_line:]

    # Set name
    name_set = False
    for n, line in enumerate(group_lines):
        if line.strip().startswith('name '):
            group_lines[n] = f' name {gizmo_name}\n'
            name_set = True
            break
    
    if not name_set:
        # Insert name after Group {
        group_lines.insert(1, f' name {gizmo_name}\n')

    # Handle help text
    help_set = False
    for n, line in enumerate(group_lines):
        if line.strip().startswith('help '):
            if help:
                help = re.sub(r"copyright", f"Copyright {get_year()}", help, flags=re.IGNORECASE)
                group_lines[n] = f' help "{help}"\n'
                help_set = True
            break

    if not help_set and help:
        help = re.sub(r"copyright", f"Copyright {get_year()}", help, flags=re.IGNORECASE)
        group_lines.insert(2, f' help "{help}"\n')
        logger.info(f"Added help message: {help}")

    # Handle tile color
    tile_color_set = False
    for n, line in enumerate(group_lines):
        if line.strip().startswith('tile_color '):
            if tile_color:
                group_lines[n] = f' tile_color {tile_color}\n'
                tile_color_set = True
                logger.info(f"Set tile color: {tile_color}")
            else:
                # Remove tile color line
                group_lines.pop(n)
                logger.info("Removed tile color")
            break

    if not tile_color_set and tile_color:
        group_lines.insert(2, f' tile_color {tile_color}\n')
        logger.info(f"Added tile color: {tile_color}")

    # Remove position data
    lines_to_remove = ['xpos', 'ypos', 'note_font']
    for attr in lines_to_remove:
        for n, line in enumerate(group_lines):
            if line.strip().startswith(f'{attr} '):
                group_lines.pop(n)
                logger.debug(f"Removed {attr}")
                break

    # Remove Viewer lines from remaining_lines
    try:
        viewer_start = remaining_lines.index(' Viewer {\n')
        viewer_lines = remaining_lines[viewer_start:]
        viewer_end = viewer_lines.index(' }\n')
        remaining_lines = remaining_lines[:viewer_start] + viewer_lines[viewer_end+1:]
        logger.debug("Removed Viewer section")
    except ValueError:
        pass  # No Viewer section

    return group_lines + remaining_lines


def sanitize_gizmo(gizmo_filepath, suffix=None, tile_color=None, help=None, rename_action="move"):
    """
    Sanitize a single gizmo file.
    
    Args:
        gizmo_filepath: Path to the .gizmo file
        suffix: Suffix to add to gizmo name (from config if None)
        tile_color: Tile color value (from config if None)
        help: Help text (from config if None)
        rename_action: "move", "backup", or None
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        logger.info(f'Processing: {gizmo_filepath}')

        # Check if this is actually a file
        if os.path.isdir(gizmo_filepath):
            return False, f"Cannot process directory as file: {gizmo_filepath}"
        
        if not os.path.isfile(gizmo_filepath):
            return False, f"Path is not a file: {gizmo_filepath}"

        # Load config for the directory containing this gizmo
        gizmo_dir = os.path.dirname(gizmo_filepath)
        config = load_config_for_directory(gizmo_dir)
        
        # Use config defaults if not provided
        suffix = suffix or config.get("suffix", "_sd")
        tile_color = tile_color or config.get("tile_color")
        help = help or config.get("help", "Copyright Sean Danischevsky")

        # Get current gizmo name
        current_gizmo_name, extension = os.path.splitext(os.path.basename(gizmo_filepath))
        
        # Sanitize filename
        sanitized_filename = sanitise_gizmo_name(current_gizmo_name, suffix)
        sanitized_gizmo_name = sanitized_filename + "1"  # Add "1" like regular nodes
        
        logger.info(f'Gizmo name: {sanitized_gizmo_name}')

        # Read file
        lines = read_file(gizmo_filepath)
        if lines is None:
            return False, f"Failed to read {gizmo_filepath}"

        # Edit the file
        lines = edit_gizmo_file(lines, sanitized_gizmo_name, tile_color=tile_color, help=help)

        # Determine output path
        gizmo_dir = os.path.dirname(gizmo_filepath)
        output_filepath = os.path.join(gizmo_dir, f"{sanitized_filename}.gizmo")
        
        # Handle renaming
        if gizmo_filepath != output_filepath:
            if rename_action == "backup":
                backup_path = gizmo_filepath + '.bkp'
                os.rename(gizmo_filepath, backup_path)
                logger.info(f'Backed up as: {backup_path}')
            elif rename_action == "move":
                if not write_file(output_filepath, lines):
                    return False, f"Failed to write {output_filepath}"
                os.remove(gizmo_filepath)
                logger.info(f'Converted to: {output_filepath}')
            else:
                return False, f'File needs renaming to: {output_filepath}'
        else:
            if not write_file(output_filepath, lines):
                return False, f"Failed to write {output_filepath}"
            logger.info(f'Saved: {output_filepath}')

        # Copy default icon
        copy_default_icon(sanitized_filename, gizmo_dir, config)
        
        return True, f"Successfully processed: {os.path.basename(output_filepath)}"

    except Exception as e:
        error_msg = f"Error processing {gizmo_filepath}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def sanitize_directory(directory_path, suffix=None, tile_color=None, help=None, rename_action="move"):
    """
    Sanitize all gizmo files in a directory recursively.
    
    Args:
        directory_path: Path to directory containing gizmos
        suffix: Suffix to add to gizmo names (from config if None)
        tile_color: Tile color value (from config if None)
        help: Help text (from config if None)
        rename_action: "move", "backup", or None
    
    Returns:
        dict: Summary of results
    """
    if not os.path.exists(directory_path):
        return {"error": f"Directory not found: {directory_path}"}

    # Load config for this directory
    config = load_config_for_directory(directory_path)
    
    # Use config defaults if not provided
    suffix = suffix or config.get("suffix", "_sd")
    tile_color = tile_color or config.get("tile_color")
    help = help or config.get("help", "Copyright Sean Danischevsky")

    results = {
        "total": 0,
        "success": 0,
        "errors": [],
        "processed": []
    }

    logger.info(f"Scanning directory: {directory_path}")

    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith('.gizmo'):
                gizmo_path = os.path.join(root, filename)
                logger.debug(f"Processing file: {gizmo_path}")
                results["total"] += 1
                
                success, message = sanitize_gizmo(
                    gizmo_path, 
                    suffix=suffix, 
                    tile_color=tile_color, 
                    help=help, 
                    rename_action=rename_action
                )
                
                if success:
                    results["success"] += 1
                    results["processed"].append(message)
                else:
                    results["errors"].append(message)

    return results


def sanitize_gizmos_unified():
    """
    Unified function to sanitize gizmos - handles files, directories, and selections.
    
    This function can process:
    - Single gizmo files
    - Multiple selected gizmo files
    - Entire directories
    - Mixed selections (files + directories)
    """
    try:
        import nuke
        
        # Check if there are selected nodes that might be gizmos
        selected_nodes = nuke.selectedNodes()
        gizmo_files = []
        
        # Look for gizmo files in selected nodes
        for node in selected_nodes:
            if node.Class() == 'Group':
                # Check if this group has a gizmo file
                node_file = node['file'].value()
                if node_file and node_file.endswith('.gizmo'):
                    gizmo_files.append(node_file)
        
        if gizmo_files:
            # Process selected gizmo files
            logger.info(f"Found {len(gizmo_files)} gizmo files in selected nodes")
            results = sanitize_multiple_files(gizmo_files)
        else:
            # Show file/directory selection dialog
            paths = nuke.getFilename("Select Gizmo Files or Directory", "*.gizmo", multiple=True)
            if not paths:
                message = "No files or directory selected"
                try:
                    nuke.message(message)
                except:
                    print(message)
                return False, message
            
            # Handle multiple selections
            all_paths = paths if isinstance(paths, list) else [paths]
            results = sanitize_multiple_paths(all_paths)
        
        # Show summary
        if results:
            summary = f"Processed {results['total']} gizmos:\n"
            summary += f"  Success: {results['success']}\n"
            summary += f"  Errors: {len(results['errors'])}\n"
            
            if results['errors']:
                summary += "\nErrors:\n"
                for error in results['errors'][:5]:  # Show first 5 errors
                    summary += f"  - {error}\n"
                if len(results['errors']) > 5:
                    summary += f"  ... and {len(results['errors']) - 5} more\n"
            
            logger.info(summary)
            
            # Show results in Nuke message dialog
            try:
                nuke.message(summary)
            except:
                # Fallback if nuke.message fails
                print(summary)
            
            return True, summary
        
        # Show message when no gizmos found
        message = "No gizmos found to process"
        try:
            nuke.message(message)
        except:
            print(message)
        return False, message
        
    except ImportError:
        return False, "Nuke not available"


def sanitize_multiple_paths(paths):
    """
    Sanitize multiple paths (files and/or directories).
    
    Args:
        paths: List of file or directory paths
    
    Returns:
        dict: Summary of results
    """
    results = {
        "total": 0,
        "success": 0,
        "errors": [],
        "processed": []
    }
    
    for path in paths:
        if os.path.isfile(path) and path.endswith('.gizmo'):
            # Single gizmo file
            success, message = sanitize_gizmo(path)
            results["total"] += 1
            if success:
                results["success"] += 1
                results["processed"].append(message)
            else:
                results["errors"].append(message)
        elif os.path.isdir(path):
            # Directory - process all gizmos in it
            dir_results = sanitize_directory(path)
            if "error" in dir_results:
                results["errors"].append(dir_results["error"])
            else:
                results["total"] += dir_results["total"]
                results["success"] += dir_results["success"]
                results["processed"].extend(dir_results["processed"])
                results["errors"].extend(dir_results["errors"])
        else:
            # Invalid path
            results["errors"].append(f"Invalid path: {path}")
    
    return results


def sanitize_multiple_files(file_paths):
    """
    Sanitize multiple gizmo files.
    
    Args:
        file_paths: List of gizmo file paths
    
    Returns:
        dict: Summary of results
    """
    results = {
        "total": 0,
        "success": 0,
        "errors": [],
        "processed": []
    }
    
    for file_path in file_paths:
        if os.path.isfile(file_path) and file_path.endswith('.gizmo'):
            success, message = sanitize_gizmo(file_path)
            results["total"] += 1
            if success:
                results["success"] += 1
                results["processed"].append(message)
            else:
                results["errors"].append(message)
        else:
            results["errors"].append(f"Invalid gizmo file: {file_path}")
    
    return results


if __name__ == '__main__':
    # Command line usage example
    import sys
    
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"Processing path: {path}")
        print(f"Is file: {os.path.isfile(path)}")
        print(f"Is directory: {os.path.isdir(path)}")
        
        if os.path.isfile(path):
            success, message = sanitize_gizmo(path)
            print(f"{'SUCCESS' if success else 'ERROR'}: {message}")
        elif os.path.isdir(path):
            results = sanitize_directory(path)
            print(f"Processed {results['total']} gizmos: {results['success']} success, {len(results['errors'])} errors")
        else:
            print(f"Path not found: {path}")
    else:
        print("Usage: python save_gizmos.py <gizmo_file_or_directory>")
        print("Or run from Nuke menu: SDNukeTools > Python > Sanitize Gizmos")




