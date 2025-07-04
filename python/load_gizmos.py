#!/usr/bin/env python3
"""
Gizmo Loader for Nuke

This script automatically loads gizmo files from organized directory structures
and adds them to the Nuke Nodes menu. It supports both the main .nuke directory
and the repos/nuketools directory structure.

Gizmos should be organized in subdirectories under 'groups' folders:
- .nuke/groups/[Category]/[gizmo_name].gizmo
- repos/nuketools/groups/[Category]/[gizmo_name].gizmo

Each gizmo should have a corresponding .png icon file with the same name.

Author: Sean Danischevsky
Date: 2022-2024
"""

import nuke
import os
import glob
import logging

# Load configuration first
try:
    import gizmo_config
    LOG_LEVEL = getattr(gizmo_config, 'LOG_LEVEL', 'INFO')
    SHOW_STATS = getattr(gizmo_config, 'SHOW_STATS', True)
    SHOW_PLACEMENT_GUIDE = getattr(gizmo_config, 'SHOW_PLACEMENT_GUIDE', True)
    CUSTOM_GIZMO_DIRECTORIES = getattr(gizmo_config, 'CUSTOM_GIZMO_DIRECTORIES', [])
    INCLUDE_CATEGORIES = getattr(gizmo_config, 'INCLUDE_CATEGORIES', [])
    EXCLUDE_CATEGORIES = getattr(gizmo_config, 'EXCLUDE_CATEGORIES', [])
    print(f"Loaded config: LOG_LEVEL = {LOG_LEVEL}")  # Debug print
except ImportError:
    # Default configuration if config file doesn't exist
    LOG_LEVEL = 'INFO'
    SHOW_STATS = True
    SHOW_PLACEMENT_GUIDE = True
    CUSTOM_GIZMO_DIRECTORIES = []
    INCLUDE_CATEGORIES = []
    EXCLUDE_CATEGORIES = []
    print(f"Using default config: LOG_LEVEL = {LOG_LEVEL}")  # Debug print

# Configure logging after configuration is loaded
logger = logging.getLogger(__name__)

# Disable propagation to root logger to avoid duplicates
logger.propagate = False

# Remove any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create a custom handler that only prints to console
class NukeConsoleHandler(logging.Handler):
    def emit(self, record):
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        level = record.levelname
        message = self.format(record)
        print(f"[{timestamp}] {level}: {message}")

# Add our custom handler
console_handler = NukeConsoleHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Set the logger level to match the configuration
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


def set_log_level(level='INFO'):
    """
    Set the log level for gizmo loading.
    
    Args:
        level (str): Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    global LOG_LEVEL
    LOG_LEVEL = level.upper()
    
    # Update the logger level
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    # Update the console handler level
    for handler in logger.handlers:
        if isinstance(handler, NukeConsoleHandler):
            handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
            break
    
    logger.info(f"Gizmo loading log level set to: {LOG_LEVEL}")


def get_log_level():
    """
    Get the current log level setting.
    
    Returns:
        str: Current log level
    """
    return LOG_LEVEL


def test_logging():
    """
    Test function to verify logging is working in Nuke.
    Run this in Nuke's script editor to test.
    """
    print("="*50)
    print("TESTING GIZMO LOADING LOGGING")
    print("="*50)
    
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    
    print(f"Current log level: {LOG_LEVEL}")
    print("="*50)


def find_gizmo_directories():
    """
    Find all potential gizmo directories in the Nuke setup.
    
    Returns:
        list: List of absolute paths to directories containing gizmos
    """
    gizmo_dirs = []
    
    # Add custom directories first
    gizmo_dirs.extend(CUSTOM_GIZMO_DIRECTORIES)
    
    # Get the main .nuke directory
    user_nuke_dir = os.path.expanduser("~/.nuke")
    
    # Check main .nuke directory
    main_groups_dir = os.path.join(user_nuke_dir, "groups")
    if os.path.exists(main_groups_dir):
        gizmo_dirs.append(main_groups_dir)
    
    # Check repos/nuketools directory
    current_dir = os.path.dirname(__file__)
    nuketools_groups_dir = os.path.join(current_dir, "..", "groups")
    if os.path.exists(nuketools_groups_dir):
        gizmo_dirs.append(os.path.abspath(nuketools_groups_dir))
    
    return gizmo_dirs


def load_gizmos(node_menu=None, gizmo_directories=None):
    """
    Load gizmos from specified directories and add them to the Nuke menu.
    
    Args:
        node_menu: Nuke menu object to add gizmos to. If None, uses the main Nodes menu.
        gizmo_directories: List of directories to search for gizmos. If None, auto-discovers.
    
    Returns:
        dict: Statistics about loaded gizmos
    """
    if node_menu is None:
        node_menu = nuke.menu('Nodes')
    
    if gizmo_directories is None:
        gizmo_directories = find_gizmo_directories()
    
    stats = {
        'total_gizmos': 0,
        'loaded_gizmos': 0,
        'missing_icons': 0,
        'errors': 0,
        'categories': set()
    }
    
    logger.debug(f"Starting to scan {len(gizmo_directories)} gizmo directories")
    
    for gizmo_dir in gizmo_directories:
        if not os.path.exists(gizmo_dir):
            logger.warning(f"Gizmo directory does not exist: {gizmo_dir}")
            continue
            
        logger.debug(f"Scanning for gizmos in: {gizmo_dir}")
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(gizmo_dir):
            for file in files:
                if file.endswith('.gizmo'):
                    stats['total_gizmos'] += 1
                    
                    try:
                        # Get gizmo name and category
                        gizmo_name = os.path.splitext(file)[0]
                        relative_path = os.path.relpath(root, gizmo_dir)
                        
                        # Determine category (subdirectory name)
                        if relative_path == '.':
                            category = 'Misc'
                        else:
                            category = relative_path.replace('/', '_').replace('\\', '_')
                        
                        # Check category filtering
                        if INCLUDE_CATEGORIES and category not in INCLUDE_CATEGORIES:
                            continue
                        if EXCLUDE_CATEGORIES and category in EXCLUDE_CATEGORIES:
                            continue
                        
                        stats['categories'].add(category)
                        
                        # Check for icon file
                        icon_path = os.path.join(root, f"{gizmo_name}.png")
                        if not os.path.exists(icon_path):
                            logger.warning(f"No icon found at {icon_path} for {gizmo_name}")
                            stats['missing_icons'] += 1
                            icon_path = None
                        
                        # Create menu path
                        if category == 'Misc':
                            menu_path = gizmo_name
                        else:
                            menu_path = f"{category}/{gizmo_name}"
                        
                        # Add to menu
                        if icon_path:
                            node_menu.addCommand(
                                menu_path, 
                                f"nuke.createNode('{gizmo_name}')", 
                                icon=icon_path
                            )
                        else:
                            node_menu.addCommand(
                                menu_path, 
                                f"nuke.createNode('{gizmo_name}')"
                            )
                        
                        # Add plugin path
                        nuke.pluginAddPath(root)
                        
                        stats['loaded_gizmos'] += 1
                        logger.debug(f"Loaded gizmo: {menu_path}")
                        
                        # Also check for additional icon formats
                        for icon_ext in ['.jpg', '.jpeg', '.tiff', '.tif']:
                            alt_icon_path = os.path.join(root, f"{gizmo_name}{icon_ext}")
                            if os.path.exists(alt_icon_path):
                                logger.debug(f"Found alternative icon format for {gizmo_name}: {alt_icon_path}")
                        
                    except Exception as e:
                        logger.error(f"Error loading gizmo {file}: {str(e)}")
                        stats['errors'] += 1
    
    return stats


def print_loading_stats(stats):
    """
    Print statistics about the gizmo loading process.
    
    Args:
        stats: Dictionary containing loading statistics
    """
    logger.info("="*50)
    logger.info("GIZMO LOADING STATISTICS")
    logger.info("="*50)
    logger.info(f"Total gizmos found: {stats['total_gizmos']}")
    logger.info(f"Successfully loaded: {stats['loaded_gizmos']}")
    logger.info(f"Missing icons: {stats['missing_icons']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info(f"Categories: {', '.join(sorted(stats['categories']))}")
    logger.info("="*50)


def print_gizmo_placement_guide():
    """
    Print a guide for where to place gizmos.
    """
    logger.info("="*50)
    logger.info("GIZMO PLACEMENT GUIDE")
    logger.info("="*50)
    logger.info("To add gizmos to your Nuke setup, place them in one of these locations:")
    logger.info("")
    logger.info("1. Main .nuke directory:")
    logger.info("   ~/.nuke/groups/[Category]/[gizmo_name].gizmo")
    logger.info("   ~/.nuke/groups/[Category]/[gizmo_name].png")
    logger.info("")
    logger.info("2. NukeTools repository:")
    logger.info("   repos/nuketools/groups/[Category]/[gizmo_name].gizmo")
    logger.info("   repos/nuketools/groups/[Category]/[gizmo_name].png")
    logger.info("")
    logger.info("Categories can be: Color, Filter, Transform, Draw, Keyer, Time, 3D, etc.")
    logger.info("Each gizmo should have a corresponding .png icon file with the same name.")
    logger.info("="*50)


if __name__ == '__main__':
    # Test logging
    logger.debug(f"Log level set to: {LOG_LEVEL}")
    logger.info("Gizmo loading system starting...")
    
    # Load gizmos and print statistics
    stats = load_gizmos()
    
    if SHOW_STATS:
        print_loading_stats(stats)
    
    # If no gizmos were found, show the placement guide
    if stats['total_gizmos'] == 0 and SHOW_PLACEMENT_GUIDE:
        print_gizmo_placement_guide()
    else:
        # Show a brief summary
        logger.info(f"Loaded {stats['loaded_gizmos']} gizmos from {len(stats['categories'])} categories")
        if stats['missing_icons'] > 0:
            logger.warning(f"{stats['missing_icons']} gizmos are missing icons")
        if stats['errors'] > 0:
            logger.error(f"{stats['errors']} gizmos failed to load")
    
    logger.info("Gizmo loading system finished.")



