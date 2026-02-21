#===============================================================================
# NUKE COLLECT FILES 1.2                                                                                  
# By Mariano Antico                                                                                       
# Barraca Post                                                                                            
# www.barraca.com.ar                                                                                      
# www.marianoantico.blogspot.com                                                                          
# Last Updated: September 21, 2011.                                                                           
# All Rights Reserved .
#  
# Description:
# Collect files of the script
#
# Tutorials:
# www.marianoantico.blogspot.com
# www.vimeo.com/29200474
#
# Supported Video Files (single-file; not treated as image sequences):
# mov, avi, mpeg, mpg, mp4, mxf, m4v, mkv, webm, R3D, r3d, braw, ari, qt
#
# Installation Notes:
# 
# 1. Copy "collectFiles.py" to nuke plugins directory (Example: "C:\Program Files\Nuke6.1v1\plugins")
# 2. Open "Init.py" located on "C:\Program Files\Nuke6.1v1\plugins"
# 3. And paste this:
# import collectFiles
# 
# 4. Save it and restart nuke
# 5. Open the Script Command window and paste this:
# collectFiles.collectFiles()
# 
# 6. Check the python button and press ok
# 
# 
# Create Menu Node:
# 
# 1. Open "Menu.py" located on "C:\Program Files\Nuke6.1v1\plugins"
# 2. And paste this at the end:
# 
# #Collect Files Menu Node
# #collectMenu = nuke.menu("File").addMenu("Collect_Files")
# #collectMenu.addCommand('Collect Files', 'seanScripts.collectFiles()')
# #collectMenu.addCommand('Help', 'collectFiles.myBlog()')
# 
# Run:
# collectFiles()                                                                                   
#===============================================================================


import nuke
import os
import sys
import shutil
import re
import glob
import subprocess
import threading
import time
import webbrowser

# Transfer mode: copy, move, symlink, hardlink
TRANSFER_MODES = ('copy', 'move', 'symlink', 'hardlink')


def _rsync_path():
    """Return path to rsync executable if available, else None."""
    if sys.platform == 'win32':
        return shutil.which('rsync') or shutil.which('rsync.exe')
    return shutil.which('rsync')


def transfer_file(src, dst, mode):
    """
    Transfer one file: copy, move, symlink, or hardlink.
    mode in TRANSFER_MODES. On failure (e.g. cross-filesystem hardlink), falls back to copy.
    """
    if mode == 'copy':
        shutil.copy2(src, dst)
        return
    if mode == 'move':
        try:
            shutil.move(src, dst)
        except OSError:
            shutil.copy2(src, dst)
            try:
                os.remove(src)
            except OSError:
                pass
        return
    if mode == 'symlink':
        try:
            target = os.path.realpath(src) if os.path.exists(src) else src
            os.symlink(target, dst)
        except OSError:
            shutil.copy2(src, dst)
        return
    if mode == 'hardlink':
        try:
            if os.path.islink(src):
                os.link(os.path.realpath(src), dst)
            else:
                os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
        return
    shutil.copy2(src, dst)


# Child Functions
def myBlog():
    url = 'http://www.marianoantico.blogspot.com/'
    webbrowser.open_new(url)

def collectPanel():
    colPanel = nuke.Panel("Collect Files 1.2 by Mariano Antico")
    colPanel.addFilenameSearch("Output Path:", "")
    rsync_available = _rsync_path() is not None
    colPanel.addEnumerationPulldown("Transfer mode:", "copy move symlink hardlink")
    colPanel.addBooleanCheckBox("Use rsync when available", rsync_available)
    colPanel.addButton("Cancel")
    colPanel.addButton("OK")

    retVar = colPanel.show()
    pathVar = colPanel.value("Output Path:")
    transfer_mode = colPanel.value("Transfer mode:").strip().lower()
    if transfer_mode not in TRANSFER_MODES:
        transfer_mode = "copy"
    use_rsync = bool(colPanel.value("Use rsync when available"))

    return (retVar, pathVar, transfer_mode, use_rsync)

# Check files
def checkForKnob(node, checkKnob ):
    try:
        node[checkKnob]
    except NameError:
        return False
    else:
        return True


def has_file_knob(node):
    """True if node has a knob named 'file' and it is a File_Knob (file path)."""
    try:
        k = node.knob('file')
        return k is not None and k.Class() == 'File_Knob'
    except Exception:
        return False


def _knob_evaluate(knob):
    """Return evaluated (resolved) value for TCL expressions; fallback to .value()."""
    try:
        if hasattr(knob, 'evaluate'):
            return knob.evaluate()
        return knob.value()
    except Exception:
        try:
            return knob.value()
        except Exception:
            return None


# Knob classes that hold text we scan for embedded file paths (labels, strings, etc.)
TEXT_KNOB_CLASSES = ('EvalString_Knob', 'String_Knob', 'Text_Knob', 'Script_Knob')


def _knob_holds_text(knob, knob_name=''):
    """True if this knob typically holds text that might contain paths (labels, etc.)."""
    try:
        if knob is None:
            return False
        if knob_name == 'label':
            return True
        return knob.Class() in TEXT_KNOB_CLASSES
    except Exception:
        return False


# Regex to find file-path-like strings in text (Unix, Windows, UNC). Excludes URLs (://).
_RE_PATH_UNIX = r'(?<![:\w])/(?:[^\s\"\'<>|*?]*/)*[^\s\"\'<>|*?]+'
_RE_PATH_WIN = r'(?<![:\w])[A-Za-z]:\\[^\s\"\'<>|*?]*(?:\\[^\s\"\'<>|*?]*)*'
_RE_PATH_UNC = r'\\\\[^\s\"\'<>|*?]+(?:\\[^\s\"\'<>|*?]*)*'
_RE_FILE_PATHS = re.compile(
    '(%s|%s|%s)' % (_RE_PATH_UNIX, _RE_PATH_WIN, _RE_PATH_UNC)
)


def _find_paths_in_text(text):
    """
    Find substrings in text that look like file paths (absolute or UNC).
    Returns list of path strings; each is stripped of surrounding whitespace.
    Skips URLs (://).
    """
    if not text or not isinstance(text, (str,)):
        return []
    out = []
    for m in _RE_FILE_PATHS.finditer(text):
        path_as_in_text = m.group(1).strip()
        if not path_as_in_text or '://' in path_as_in_text:
            continue
        out.append(path_as_in_text)
    return out


def _path_is_sequence(p, path_is_sequence_fn=None):
    """True if path contains a sequence placeholder (%0xd or #)."""
    if not p:
        return False
    base = os.path.basename(p)
    if re.search(r'%\d*d', base) or '#' in base:
        return True
    return False


def _sequence_frame_file_path(seq_path, seq_dir, frame, pad):
    """Return full path to one frame of a sequence (for size check or copy)."""
    base = seq_path.split("/")[-1]
    if pad and re.search(re.escape(pad), base):
        base = base.replace(pad, str(pad % frame))
    elif '#' in base:
        m = re.search(r'#+', base)
        if m:
            n = len(m.group())
            base = re.sub(r'#+', str(frame).zfill(n), base, count=1)
    return os.path.join(seq_dir, base)


def _sequence_frames_on_disk(fileNodePath, paddings):
    """
    Given a sequence path (e.g. /path/to/shot.%04d.exr), list all frame numbers
    that exist on disk in that directory. Returns (seq_dir_path, list_of_frame_numbers).
    """
    parts = fileNodePath.split("/")
    if len(parts) < 2:
        return None, []
    dir_path = "/".join(parts[:-1])
    filename = parts[-1]
    if not os.path.isdir(dir_path):
        return dir_path, []
    frame_numbers = []
    # Build glob: shot.%04d.exr or shot.####.exr -> shot.*.exr
    glob_pattern = re.sub(r'%\d*d', '*', filename)
    if '#' in filename:
        glob_pattern = re.sub(r'#+', '*', glob_pattern)
    has_placeholder = '*' in glob_pattern
    if has_placeholder:
        full_glob = os.path.join(dir_path, glob_pattern)
        for f in glob.glob(full_glob):
            base = os.path.basename(f)
            m = re.search(r'(\d+)(?=\D*\.\w+$|\D*$)', base)
            if m:
                frame_numbers.append(int(m.group(1)))
        return dir_path, sorted(set(frame_numbers))
    return dir_path, []


def _collect_preflight(nuke_nodes, videoExtension, paddings):
    """
    First pass: gather every file/sequence we would copy and check existence.
    Returns (single_files, sequences, embedded_files, warnings).
    - single_files: list of dicts {path, dest_name, exists, node}
    - sequences: list of dicts {path, dir, node_first, node_last, frames_on_disk, ...}
    - embedded_files: list of dicts {node, knob_name, path_as_in_text, path_norm, dest_name, exists} for paths found in text knobs
    - warnings: list of strings
    """
    def path_is_sequence(p):
        return _path_is_sequence(p)

    single_files = []
    sequences = []
    embedded_files = []
    warnings = []
    seen_seq_dirs = set()

    for fileNode in nuke_nodes:
        if not has_file_knob(fileNode) or checkForKnob(fileNode, 'Render'):
            continue
        fileNodePath = _knob_evaluate(fileNode['file'])
        if fileNodePath is None:
            continue
        fileNodePath = str(fileNodePath).strip()
        if not fileNodePath:
            continue
        readFilename = fileNodePath.split("/")[-1]
        pathLower = fileNodePath.lower()
        is_video = any(pathLower.endswith('.' + ext.lower()) for ext in videoExtension)

        if checkForKnob(fileNode, 'first'):
            if is_video and not path_is_sequence(fileNodePath):
                # Single video file
                single_files.append({
                    'path': fileNodePath,
                    'dest_name': readFilename,
                    'exists': os.path.isfile(fileNodePath),
                    'node': fileNode,
                })
                if not os.path.isfile(fileNodePath):
                    warnings.append("MISSING: %s" % fileNodePath)
            else:
                first_val = _knob_evaluate(fileNode['first'])
                last_val = _knob_evaluate(fileNode['last'])
                try:
                    frameFirst = int(first_val) if first_val is not None else 0
                    frameLast = int(last_val) if last_val is not None else 0
                except (TypeError, ValueError):
                    frameFirst = frameLast = 0
                if frameFirst == frameLast:
                    single_files.append({
                        'path': fileNodePath,
                        'dest_name': readFilename,
                        'exists': os.path.isfile(fileNodePath),
                        'node': fileNode,
                    })
                    if not os.path.isfile(fileNodePath):
                        warnings.append("MISSING: %s" % fileNodePath)
                elif path_is_sequence(fileNodePath):
                    seq_dir, frames_on_disk = _sequence_frames_on_disk(fileNodePath, paddings)
                    matched_pad = None
                    for pad in paddings:
                        if re.search(re.escape(pad), fileNodePath.split("/")[-1]):
                            matched_pad = pad
                            break
                    dirSeq = fileNodePath.split("/")[-2] + '/'
                    key = (seq_dir, dirSeq)
                    missing_in_range = [fr for fr in range(frameFirst, frameLast + 1) if fr not in frames_on_disk]
                    extra_below = [f for f in frames_on_disk if f < frameFirst]
                    extra_above = [f for f in frames_on_disk if f > frameLast]
                    extra_outside = extra_below or extra_above
                    if missing_in_range:
                        warnings.append("SEQUENCE (script range %s-%s): Missing frames on disk: %s ... (%s total). Path: %s" % (
                            frameFirst, frameLast,
                            missing_in_range[:5] if len(missing_in_range) > 5 else missing_in_range,
                            len(missing_in_range),
                            fileNodePath
                        ))
                    if extra_outside:
                        warnings.append("SEQUENCE (script range %s-%s): Directory has frames outside range: %s ... (%s extra). Path: %s" % (
                            frameFirst, frameLast,
                            (extra_below[:3] + ['...'] + extra_above[-3:]) if (len(extra_below) + len(extra_above)) > 7 else (extra_below + extra_above),
                            len(extra_outside),
                            fileNodePath
                        ))
                    if key not in seen_seq_dirs:
                        seen_seq_dirs.add(key)
                        sequences.append({
                            'path': fileNodePath,
                            'dir': seq_dir,
                            'dirSeq': dirSeq,
                            'node_first': frameFirst,
                            'node_last': frameLast,
                            'frames_on_disk': frames_on_disk,
                            'extra_outside_range': bool(extra_outside),
                            'node': fileNode,
                            'pad': matched_pad,
                            'paddings': paddings,
                            'readFilename': readFilename,
                        })
                    else:
                        # Merge range with existing entry (same sequence, different Read node range)
                        for s in sequences:
                            if (s['dir'], s['dirSeq']) == key:
                                s['node_first'] = min(s['node_first'], frameFirst)
                                s['node_last'] = max(s['node_last'], frameLast)
                                s['extra_outside_range'] = s['extra_outside_range'] or bool(extra_outside)
                                break
                else:
                    # Video with first/last but no sequence placeholder
                    single_files.append({
                        'path': fileNodePath,
                        'dest_name': readFilename,
                        'exists': os.path.isfile(fileNodePath),
                        'node': fileNode,
                    })
                    if not os.path.isfile(fileNodePath):
                        warnings.append("MISSING: %s" % fileNodePath)
        else:
            single_files.append({
                'path': fileNodePath,
                'dest_name': readFilename,
                'exists': os.path.isfile(fileNodePath),
                'node': fileNode,
            })
            if not os.path.isfile(fileNodePath):
                warnings.append("MISSING: %s" % fileNodePath)

    # Scan text knobs (labels, string knobs, etc.) for embedded file paths
    seen_missing_embedded = set()
    for node in nuke_nodes:
        try:
            for kname in node.knobs():
                k = node.knob(kname)
                if not _knob_holds_text(k, kname):
                    continue
                try:
                    val = _knob_evaluate(k)
                    if val is None or not isinstance(val, str):
                        continue
                except Exception:
                    continue
                for path_as_in_text in _find_paths_in_text(val):
                    path_norm = os.path.normpath(path_as_in_text.strip()).strip()
                    if not path_norm:
                        continue
                    dest_name = os.path.basename(path_norm)
                    exists = os.path.isfile(path_norm)
                    if not exists and path_norm not in seen_missing_embedded:
                        seen_missing_embedded.add(path_norm)
                        warnings.append("MISSING (in text %s.%s): %s" % (node.name(), kname, path_as_in_text))
                    embedded_files.append({
                        'node': node,
                        'knob_name': kname,
                        'path_as_in_text': path_as_in_text,
                        'path_norm': path_norm,
                        'dest_name': dest_name,
                        'exists': exists,
                    })
        except Exception:
            pass

    return single_files, sequences, embedded_files, warnings


# Parent Function
def collectFiles():
    panelResult = collectPanel()
    if len(panelResult) == 4:
        retVar, pathVar, transfer_mode, use_rsync = panelResult
    else:
        retVar, pathVar = panelResult[0], panelResult[1]
        transfer_mode, use_rsync = 'copy', bool(_rsync_path())

    #copy script to target directory
    script2Copy = nuke.root()['name'].value()
    scriptName = os.path.basename(nuke.Root().name())

    fileNames = []
    paddings = ['%01d', '%02d', '%03d', '%04d', '%05d', '%06d', '%07d', '%08d', '%d', '%1d']
    # Single-file video extensions (copy one file; do not treat as image sequence)
    videoExtension = [
        'mov', 'avi', 'mpeg', 'mpg', 'mp4', 'mxf', 'm4v', 'mkv', 'webm',
        'R3D', 'r3d', 'braw', 'ari', 'qt'
    ]
    def path_is_sequence(p):
        return _path_is_sequence(p)

    cancelCollect = 0
    rsync_exe = _rsync_path() if use_rsync else None

    # hit OK
    if retVar == 1 and pathVar != '':
        targetPath = pathVar

        # Check to make sure a file path is not passed through
        if os.path.isfile(targetPath):
            targetPath = os.path.dirname(targetPath)

        # Make sure target path ends with a slash (for consistency)
        if not targetPath.endswith('/'):
            targetPath += '/'

        # Check if local directory already exists. Ask to create it if it doesn't
        if not os.path.exists(targetPath):
            if nuke.ask("Directory does not exist. Create now?"):
                try:
                    os.makedirs(targetPath)
                except:
                    raise Exception("Can't make target directory!")
                    return False
            else:
                nuke.message("Cannot proceed without valid target directory.")
                return False

        # ----- Pre-flight: check all files and build warnings before any copy -----
        single_files, sequences, embedded_files, warnings = _collect_preflight(
            nuke.allNodes(), videoExtension, paddings
        )
        for w in warnings:
            print(w)

        # Rough transfer size: file count and total bytes
        unique_embedded_paths = set(e['path_norm'] for e in embedded_files)
        num_files = (len(single_files) + len(unique_embedded_paths) +
                     sum(len(s.get('frames_on_disk', [])) for s in sequences))
        total_bytes = 0
        for item in single_files:
            if item.get('exists') and os.path.isfile(item['path']):
                try:
                    total_bytes += os.path.getsize(item['path'])
                except Exception:
                    pass
        for path_norm in unique_embedded_paths:
            if os.path.isfile(path_norm):
                try:
                    total_bytes += os.path.getsize(path_norm)
                except Exception:
                    pass
        for seq in sequences:
            for frame in seq.get('frames_on_disk', []):
                path = _sequence_frame_file_path(
                    seq['path'], seq['dir'], frame, seq.get('pad'))
                if os.path.isfile(path):
                    try:
                        total_bytes += os.path.getsize(path)
                    except Exception:
                        pass
        size_gb = total_bytes / (1024.0 ** 3)

        summary = "Single: %s  |  Sequences: %s  |  In text: %s  |  Warnings: %s  |  ~%s files  |  ~%.2f GB" % (
            len(single_files), len(sequences), len(embedded_files), len(warnings), num_files, size_gb)
        print(summary)
        # Show full warnings in a multiline panel so user can scroll through all issues
        warn_lines = [
            "=== Pre-flight summary ===",
            summary,
            "",
            "~%s files  |  ~%.2f GB transfer" % (num_files, size_gb),
            "",
            "=== Warnings (%s) ===" % len(warnings) if warnings else "=== No warnings ===",
        ]
        if warnings:
            warn_lines.append("")
            warn_lines.extend(warnings)
        else:
            warn_lines.append("None")
        full_text = "\n".join(warn_lines)
        try:
            warn_panel = nuke.Panel("Collect Files - Pre-flight")
            if hasattr(warn_panel, 'addMultilineTextInput'):
                warn_panel.addMultilineTextInput("Issues", full_text)
            else:
                warn_panel.addNotepad("Issues", full_text)
            warn_panel.addButton("Cancel")
            warn_panel.addButton("Proceed")
            if warn_panel.show() != 1:
                print("COLLECT CANCELLED (user declined)")
                return False
        except Exception:
            if not nuke.ask(full_text[:500] + ("\n\n... (see Script Editor for full list)\n\nProceed with copy?" if len(full_text) > 500 else "\n\nProceed with copy?")):
                print("COLLECT CANCELLED (user declined)")
                return False
        copy_whole_sequence_dirs = False
        if any(s.get('extra_outside_range') for s in sequences):
            copy_whole_sequence_dirs = nuke.ask(
                "Some sequences have files on disk outside the Read node's first/last range.\n\n"
                "Copy entire directory (all files) for these sequences?\n\n"
                "Yes = copy whole directory\nNo = copy only frames in script range"
            )

        # ----- Proceed with copy -----
        scriptName = os.path.basename(nuke.Root().name())
        footagePath = targetPath + 'footage/'
        if not os.path.exists(footagePath):
            os.mkdir(footagePath)

        # Unique embedded paths to copy (path_norm -> dest_name)
        unique_embedded = {}
        for e in embedded_files:
            p, d = e['path_norm'], e['dest_name']
            if p not in unique_embedded:
                unique_embedded[p] = d

        task = nuke.ProgressTask("Collect Files 1.2")
        try:
            total = (len(single_files) + len(unique_embedded) +
                     sum(max(1, len(s.get('frames_on_disk', []))) for s in sequences))
            done = 0

            # Copy single files
            for item in single_files:
                if task.isCancelled():
                    cancelCollect = 1
                    break
                path, dest_name, exists, _ = item['path'], item['dest_name'], item['exists'], item['node']
                newFilenamePath = footagePath + dest_name
                task.setMessage("Collecting: " + dest_name)
                task.setProgress(int(done * 100 / max(1, total)))
                if os.path.exists(newFilenamePath):
                    print((newFilenamePath + '     DUPLICATED'))
                elif exists:
                    transfer_file(path, newFilenamePath, transfer_mode)
                    print((newFilenamePath + '     COPIED'))
                else:
                    print((newFilenamePath + '     MISSING'))
                done += 1

            # Copy files found in text knobs (labels, string knobs, etc.)
            for path_norm, dest_name in unique_embedded.items():
                if task.isCancelled():
                    cancelCollect = 1
                    break
                newFilenamePath = footagePath + dest_name
                task.setMessage("Collecting (from text): " + dest_name)
                task.setProgress(int(done * 100 / max(1, total)))
                if os.path.exists(newFilenamePath):
                    print((newFilenamePath + '     DUPLICATED'))
                elif os.path.isfile(path_norm):
                    transfer_file(path_norm, newFilenamePath, transfer_mode)
                    print((newFilenamePath + '     COPIED'))
                else:
                    print((newFilenamePath + '     MISSING'))
                done += 1

            # Copy sequences (whole directory or script range only)
            for seq in sequences:
                if task.isCancelled():
                    cancelCollect = 1
                    break
                fileNodePath = seq['path']
                dirSeq = seq['dirSeq']
                node_first = seq['node_first']
                node_last = seq['node_last']
                frames_on_disk = seq['frames_on_disk']
                pad = seq['pad']
                newFilenamePath = footagePath + dirSeq
                if not os.path.exists(newFilenamePath):
                    os.mkdir(newFilenamePath)
                # Copy whole directory; only limit to script range if user said No to extra frames
                if seq.get('extra_outside_range') and not copy_whole_sequence_dirs:
                    frames_to_copy = [f for f in frames_on_disk if node_first <= f <= node_last]
                else:
                    frames_to_copy = frames_on_disk
                # Use rsync for whole-dir copy/move when available
                use_rsync_here = (rsync_exe and transfer_mode in ('copy', 'move') and
                                  frames_to_copy == frames_on_disk and len(frames_to_copy) > 0)
                if use_rsync_here:
                    src_dir = seq['dir'].rstrip(os.sep) + os.sep
                    try:
                        cmd = [rsync_exe, '-a', '--progress', src_dir, newFilenamePath]
                        task.setMessage("Rsync: " + dirSeq)
                        subprocess.run(cmd, check=True, timeout=3600)
                        for _ in frames_to_copy:
                            done += 1
                        print((newFilenamePath + '     RSYNC (directory)'))
                        if transfer_mode == 'move':
                            for frame in frames_to_copy:
                                fp = _sequence_frame_file_path(fileNodePath, seq['dir'], frame, pad)
                                try:
                                    if os.path.isfile(fp):
                                        os.remove(fp)
                                except OSError:
                                    pass
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
                        use_rsync_here = False
                        print("Rsync failed (%s), falling back to per-file" % e)
                if not use_rsync_here:
                    for frame in frames_to_copy:
                        if task.isCancelled():
                            cancelCollect = 1
                            break
                        originalSeq = _sequence_frame_file_path(
                            fileNodePath, seq['dir'], frame, pad)
                        frameSeq = os.path.basename(originalSeq)
                        newSeq = newFilenamePath + frameSeq
                        task.setMessage("Collecting: " + frameSeq)
                        task.setProgress(int(done * 100 / max(1, total)))
                        if os.path.exists(newSeq):
                            print((newSeq + '     DUPLICATED'))
                        elif os.path.exists(originalSeq):
                            transfer_file(originalSeq, newSeq, transfer_mode)
                            print((newSeq + '     COPIED'))
                        else:
                            print((newSeq + '     MISSING'))
                        done += 1
                print('')

            if (cancelCollect == 0):
                # Save script to archive path
                newScriptPath = targetPath + scriptName
                nuke.scriptSaveAs(newScriptPath)
    
                #link files to new path
                for fileNode in nuke.allNodes():
                    if has_file_knob(fileNode):
                        if not checkForKnob(fileNode, 'Render'):
                            fileNodePath = fileNode['file'].value()
                            if (fileNodePath == ''):
                                continue
                            else:
                                
                                if checkForKnob(fileNode, 'first'):
                                    pathLower = fileNodePath.lower()
                                    isVideoFile = any(pathLower.endswith('.' + ext.lower()) for ext in videoExtension)
                                    if isVideoFile and not path_is_sequence(fileNodePath):
                                        fileNodePath = fileNode['file'].value()
                                        readFilename = fileNodePath.split("/")[-1]
                                        reloadPath = '[file dirname [value root.name]]/footage/' + readFilename
                                        fileNode['file'].setValue(reloadPath)
                                    else:
                                        # frame range: single frame or sequence
                                        frameFirst = int(fileNode['first'].value())
                                        frameLast = int(fileNode['last'].value())
                                        if (frameFirst == frameLast):
                                            fileNodePath = fileNode['file'].value()
                                            readFilename = fileNodePath.split("/")[-1]
                                            reloadPath = '[file dirname [value root.name]]/footage/' + readFilename
                                            fileNode['file'].setValue(reloadPath)
                                        elif path_is_sequence(fileNodePath):
                                            fileNodePath = fileNode['file'].value()
                                            dirSeq = fileNodePath.split("/")[-2] + '/'
                                            readFilename = fileNodePath.split("/")[-1]
                                            reloadPath = '[file dirname [value root.name]]/footage/' + dirSeq + readFilename
                                            fileNode['file'].setValue(reloadPath)
                                        else:
                                            fileNodePath = fileNode['file'].value()
                                            readFilename = fileNodePath.split("/")[-1]
                                            reloadPath = '[file dirname [value root.name]]/footage/' + readFilename
                                            fileNode['file'].setValue(reloadPath)
                                
                                else:
                                    fileNodePath = fileNode['file'].value()
                                    readFilename = fileNodePath.split("/")[-1]
                                    reloadPath = '[file dirname [value root.name]]/footage/' + readFilename
                                    fileNode['file'].setValue(reloadPath)
                        else:
                            pass
                    else:
                        pass

                # Rewrite paths in text knobs (labels, etc.) to point at collected footage
                new_path_prefix = '[file dirname [value root.name]]/footage/'
                for e in embedded_files:
                    try:
                        node, kname = e['node'], e['knob_name']
                        path_as_in_text = e['path_as_in_text']
                        dest_name = e['dest_name']
                        new_path = new_path_prefix + dest_name
                        k = node.knob(kname)
                        if k is None:
                            continue
                        try:
                            raw = k.getValue() if hasattr(k, 'getValue') else k.value()
                        except Exception:
                            raw = k.value()
                        if not isinstance(raw, str) or path_as_in_text not in raw:
                            continue
                        new_val = raw.replace(path_as_in_text, new_path, 1)
                        if hasattr(k, 'setValue'):
                            k.setValue(new_val)
                        elif hasattr(k, 'setText'):
                            k.setText(new_val)
                    except Exception:
                        pass

                nuke.scriptSave()
                print ('COLLECT DONE!!')
                nuke.message('COLLECT DONE!!')

            else:
                print ('COLLECT CANCELLED - Toma Rojo Puto')
                nuke.message('COLLECT CANCELLED')
        finally:
            task.setProgress(100)
            del task

    # If they just hit OK on the default ellipsis...
    elif retVar == 1 and pathVar == '':
        nuke.message("Select a path")
        return False

    # hit CANCEL
    else:
        print('COLLECT CANCELLED')
