"""
Read from Write - Create Read nodes from Write nodes and similar conversions.

Supported conversions:
    Write/WriteTank -> Read
    Read -> Read (reload with updated frame range)
    GenerateLUT -> OCIOFileTransform
    WriteGeo -> ReadGeo
    SmartVector -> SmartVector

Sean Danischevsky 2016
"""

import os
import re
import nuke

MOVIE_EXTENSIONS = [
    '.qt', '.mov', '.mxf', '.mp4', '.avi', '.m4v',
    '.mkv', '.webm', '.r3d', '.braw', '.ari'
]

# Mapping of node classes to their reader node types
NODE_READER_MAP = {
    'GenerateLUT': 'OCIOFileTransform',
    'SmartVector': 'SmartVector',
    'WriteGeo': 'ReadGeo',
}


def _create_reader_node(node, reader_class):
    """Create a reader node from a source node's file path."""
    try:
        filepath = node['file'].value()
        reader = getattr(nuke.nodes, reader_class)()
        reader['file'].setValue(filepath)
        reader.setXYpos(node.xpos(), node.ypos() + node.screenHeight())
        return reader
    except Exception as e:
        return e


def _find_sequence_path(filepath):
    """
    Find a matching file sequence in the directory for a given filepath.
    
    For movie files, returns the filepath unchanged.
    For image sequences, finds the matching sequence pattern in the directory.
    
    Returns the path with frame range notation (e.g. 'file.%04d.exr 1-100').
    Raises FileNotFoundError if no matching files found.
    """
    dirpath, basepath = os.path.split(os.path.abspath(filepath))
    base, extension = os.path.splitext(basepath)
    
    # Clean extension (handles 'None - None' problem from ShotGrid/Nuke)
    extension = re.sub(r' .+', '', extension)

    # Movie files don't need sequence detection
    if extension in MOVIE_EXTENSIONS:
        return filepath

    # Args: dir, splitSequences, extraInformation, returnDirs, returnHidden
    dir_contents = nuke.getFileNameList(dirpath, False, False, False, False)
    
    # Build regex pattern: strip trailing numbers, escape dots, match extension
    match_pattern, had_numbers = re.subn(r'\d+$', '', base)
    match_pattern = re.sub(r'\.', r'\.', match_pattern)
    
    if had_numbers:
        match_pattern += ".+"  # Match frame numbers
    
    match_pattern += extension + ".*"  # Match extension and optional frame range
    
    matches = [f for f in dir_contents if re.match(match_pattern, f)]
    
    if not matches:
        raise FileNotFoundError(f"No matching files found for: {filepath}")

    return os.path.join(dirpath, matches[0])


def _copy_colorspace(source_node, target_node):
    """Copy colorspace from source to target, handling 'default (...)' format."""
    colorspace = source_node['colorspace'].value()
    
    if colorspace == "default" or target_node['colorspace'].value() == colorspace:
        return
    
    # Extract colorspace from "default (colorspace)" format
    match = re.match(r"default \((.+)\)", colorspace)
    if match:
        colorspace = match.group(1)
    
    target_node['colorspace'].setValue(colorspace)


def readFromWrite(node):
    """Create a Read node from a Write node, matching the rendered file sequence."""
    try:
        # Get evaluated filepath (with frame number substituted)
        filepath = nuke.filename(node, nuke.REPLACE)
        
        # Resolve to sequence path BEFORE creating Read (avoids blank nodes on failure)
        resolved_filepath = _find_sequence_path(filepath)
        
        read = nuke.nodes.Read()
        read['file'].fromUserText(resolved_filepath)
        read.setXYpos(node.xpos(), node.ypos() + read.screenHeight())
        
        _copy_colorspace(node, read)
        
        return read

    except Exception as e:
        return e


def updateRead(node):
    """Refresh an existing Read node to detect updated frame ranges."""
    filepath = nuke.filename(node, nuke.REPLACE)
    extension = os.path.splitext(filepath)[1].lower()
    
    if extension in MOVIE_EXTENSIONS:
        # Movies: fromUserText doesn't re-detect duration on existing nodes.
        # Create a temp Read to get the correct frame count, then copy it.
        original_path = node['file'].value()
        temp_read = nuke.nodes.Read()
        temp_read['file'].fromUserText(original_path)
        
        node['first'].setValue(temp_read['first'].value())
        node['last'].setValue(temp_read['last'].value())
        node['origfirst'].setValue(temp_read['origfirst'].value())
        node['origlast'].setValue(temp_read['origlast'].value())
        
        nuke.delete(temp_read)
    else:
        # Sequences: re-detect the frame range from disk
        try:
            resolved_filepath = _find_sequence_path(filepath)
            node['file'].fromUserText(resolved_filepath)
        except FileNotFoundError:
            pass  # Keep existing file path if no matches found
    
    node['reload'].execute()
    return node


def readFromWrites(nodes):
    """
    Process multiple nodes, creating appropriate reader nodes for each.
    
    Returns a list of successfully created nodes.
    """
    successful = []
    
    for node in nodes:
        node_class = node.Class()
        
        if node_class in ['Write', 'WriteTank']:
            result = readFromWrite(node)
        elif node_class in NODE_READER_MAP:
            result = _create_reader_node(node, NODE_READER_MAP[node_class])
        elif node_class == 'Read':
            result = updateRead(node)
        elif 'file' in node.knobs():
            # Only try unknown nodes if they have a file knob
            result = readFromWrite(node)
        else:
            continue  # Skip nodes without file knobs

        if isinstance(result, nuke.Node):
            successful.append(result)
    
    return successful
