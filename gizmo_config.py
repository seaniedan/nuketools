#!/usr/bin/env python3
"""
Gizmo Loading Configuration

This file contains configuration options for the gizmo loading system.
Modify these settings to control how gizmos are loaded and what information is displayed.
"""

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

# Directories to scan for gizmos (leave empty for auto-discovery)
# Example: ['/path/to/custom/gizmos', '/another/path']
CUSTOM_GIZMO_DIRECTORIES = []

# Categories to include (leave empty for all categories)
# Example: ['Color', 'Filter', 'Transform']
INCLUDE_CATEGORIES = []

# Categories to exclude
# Example: ['Deprecated', 'Old']
EXCLUDE_CATEGORIES = [] 