import datetime
import os
import re
import shutil
import subprocess
import tempfile

import nuke


# raster stills ffmpeg can read straight off disk (no Nuke render needed)
LDR_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}

# common install locations to check when ffmpeg isn't on PATH (Nuke launched
# from the Dock/Finder doesn't inherit the shell PATH, so Homebrew's
# /opt/homebrew/bin is usually missing)
_FFMPEG_FALLBACKS = ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/usr/bin/ffmpeg")


def _ffmpeg_bin():
    # resolved ffmpeg path, or None if it genuinely can't be found
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in _FFMPEG_FALLBACKS:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def _safe_name(raw_name):
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_name.strip())
    return cleaned or "node"


def _default_output_dir():
    script_path = nuke.root().name()
    if script_path and script_path != "Root":
        return os.path.join(os.path.dirname(script_path), "node_gifs")
    return os.path.join(os.path.expanduser("~"), "node_gifs")


def _hashes_to_printf(path):
    # turn a Nuke frame token (#### or %0Nd) into a printf pattern ffmpeg/python
    # can fill per frame. returns (printf_path, pad) or None if there's no token.
    m = re.search(r"#+", path)
    if m:
        pad = len(m.group(0))
        return path[: m.start()] + "%0{}d".format(pad) + path[m.end():], pad
    m = re.search(r"%0(\d+)d", path)
    if m:
        return path, int(m.group(1))
    return None


def _read_sequence_pattern(node, first):
    # if node is a Read pointing at an existing 8-bit still sequence, return a
    # printf path we can resolve per frame; otherwise None (so we render).
    if node.Class() != "Read":
        return None
    raw = node["file"].value()
    if not raw:
        return None
    if os.path.splitext(raw)[1].lower() not in LDR_EXTS:
        return None
    conv = _hashes_to_printf(raw)
    if not conv:
        return None
    pattern, _pad = conv
    try:
        if not os.path.isfile(pattern % first):
            return None
    except Exception:
        return None
    return pattern


def _has_alpha(node):
    # True if the node exposes an alpha channel (which a GIF can't carry and
    # which makes ffmpeg's palette come out wrong if fed straight through)
    try:
        return any(c.endswith(".alpha") for c in node.channels())
    except Exception:
        return False


def _run_ffmpeg(sequence_glob, palette_path, output_gif, fps, ffmpeg=None):
    ffmpeg = ffmpeg or _ffmpeg_bin() or "ffmpeg"
    palette_cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-pattern_type", "glob",
        "-i", sequence_glob,
        "-vf", "palettegen",
        palette_path,
    ]
    gif_cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-pattern_type", "glob",
        "-i", sequence_glob,
        "-i", palette_path,
        "-lavfi", "paletteuse",
        "-loop", "0",
        output_gif,
    ]
    subprocess.run(palette_cmd, check=True, capture_output=True, text=True)
    subprocess.run(gif_cmd, check=True, capture_output=True, text=True)


def _selection_range(nodes):
    # union range of the selected nodes (min first, max last), used as the
    # default in the panel; None if no node reports a usable range
    firsts, lasts = [], []
    for n in nodes:
        try:
            firsts.append(int(n.firstFrame()))
            lasts.append(int(n.lastFrame()))
        except Exception:
            continue
    if not firsts:
        return None
    return min(firsts), max(lasts)


def _parse_range(text):
    # accept "1-100", "1 100" or "1,100"; return (first, last) or None
    if not text:
        return None
    parts = re.split(r"[-,\s]+", text.strip())
    parts = [p for p in parts if p]
    try:
        if len(parts) == 1:
            v = int(parts[0])
            return v, v
        if len(parts) >= 2:
            return int(parts[0]), int(parts[1])
    except ValueError:
        return None
    return None


def _playback_order(first, last, playback):
    # forward frames for a loop; forward then back (excluding the two end frames
    # so they don't dwell) for a bounce.
    frames = list(range(first, last + 1))
    if playback == "bounce" and len(frames) > 2:
        frames = frames + list(reversed(frames[1:-1]))
    return frames


def render_selected_nodes_to_looping_gifs(output_dir=None, first_frame=None,
                                          last_frame=None, fps=None,
                                          playback=None, keep_frames=None):
    """
    Render one animated GIF per selected node.

    A single dialog (shown once per call) chooses loop/bounce playback, the
    fps, the frame range (defaulting to the selected nodes' input range), and
    whether to keep the generated frames. A Read of an 8-bit still sequence is
    fed straight to ffmpeg (no re-render). Each finished GIF is read back in as
    a Read node.
    """
    selected_nodes = nuke.selectedNodes()
    if not selected_nodes:
        nuke.message("Select at least one node to render GIFs.")
        return []

    ffmpeg = _ffmpeg_bin()
    if not ffmpeg:
        nuke.message(
            "ffmpeg is required to build GIFs on this setup.\n"
            "Install ffmpeg, then run this command again."
        )
        return []

    output_dir = output_dir or _default_output_dir()
    os.makedirs(output_dir, exist_ok=True)

    # progress to the Script Editor / terminal, so a failed run (e.g. ffmpeg
    # complaining about a mov's frames) leaves a trail to read
    def _log(msg):
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        nuke.tprint("{}  {}".format(stamp, msg))

    _log("run: {} node(s), ffmpeg={}".format(
        len(selected_nodes), ffmpeg))

    root_fps = float(nuke.root()["fps"].value())

    # one modal per call (skipped when called with explicit args, e.g. tests)
    if playback is None:
        default_range = _selection_range(selected_nodes)
        range_default = ("{}-{}".format(*default_range) if default_range else "")
        panel = nuke.Panel("Selected nodes to GIF")
        panel.addEnumerationPulldown("playback", "loop bounce")
        panel.addSingleLineInput("fps", str(fps if fps is not None else root_fps))
        panel.addSingleLineInput("range", range_default)
        panel.addBooleanCheckBox("keep generated frames", False)
        if not panel.show():
            return []
        playback = panel.value("playback")
        try:
            fps_value = float(panel.value("fps"))
        except (TypeError, ValueError):
            fps_value = root_fps
        # a range typed here applies to every selected node; leaving it as the
        # default (or clearing it) keeps each node on its own input range
        parsed_range = _parse_range(panel.value("range"))
        if parsed_range is not None:
            first_frame, last_frame = parsed_range
        keep = str(panel.value("keep generated frames")).lower() in ("1", "true")
    else:
        fps_value = float(fps) if fps is not None else root_fps
        keep = bool(keep_frames)

    if fps_value <= 0:
        fps_value = root_fps
    if playback not in ("loop", "bounce"):
        playback = "loop"

    created_paths = []
    kept_dirs = []
    new_reads = []
    failed_nodes = []

    for node in selected_nodes:
        # each node over its OWN range unless an explicit range was passed in
        first = int(first_frame if first_frame is not None else node.firstFrame())
        last = int(last_frame if last_frame is not None else node.lastFrame())
        _log("{} [{}]: range {}-{}".format(node.fullName(), node.Class(), first, last))
        if first > last:
            _log("  skipping: frame range {}-{} is invalid".format(first, last))
            failed_nodes.append(node.fullName())
            continue

        output_path = os.path.join(output_dir, "{}.gif".format(_safe_name(node.fullName())))
        work_dir = tempfile.mkdtemp(prefix="nuke_gif_", dir=output_dir)
        seq_dir = os.path.join(work_dir, "seq")
        os.makedirs(seq_dir)

        write_node = None
        rendered_dir = None
        try:
            # decide the per-frame source: reuse a Read's stills, else render
            reuse_pattern = _read_sequence_pattern(node, first)
            if reuse_pattern is not None:
                # on-disk stills are fed straight to ffmpeg (no re-render), so
                # an alpha channel would corrupt the palette. Warn before using.
                if _has_alpha(node) and not nuke.ask(
                    "{} has an alpha channel.\n"
                    "GIFs are RGB only, and alpha usually makes the colours "
                    "come out wrong.\n\nEncode this sequence anyway?".format(
                        node.fullName())
                ):
                    _log("  skipping: alpha channel, user declined")
                    failed_nodes.append(node.fullName())
                    continue
                _log("  reusing on-disk sequence: {}".format(reuse_pattern))
                src_ext = os.path.splitext(reuse_pattern)[1].lower()
                def source_for(frame, _p=reuse_pattern):
                    return _p % frame
            else:
                _log("  rendering frames to png (not an on-disk still sequence)")
                src_ext = ".png"
                rendered_dir = os.path.join(work_dir, "frames")
                os.makedirs(rendered_dir)
                render_pattern = os.path.join(rendered_dir, "frame.%04d.png")
                nuke_pattern = os.path.join(rendered_dir, "frame.####.png")

                write_node = nuke.nodes.Write()
                write_node["file"].fromUserText(nuke_pattern)
                write_node.setInput(0, node)
                write_node["file_type"].setValue("png")
                write_node["channels"].setValue("rgb")
                if "create_directories" in write_node.knobs():
                    write_node["create_directories"].setValue(True)
                nuke.execute(write_node, first, last)

                def source_for(frame, _p=render_pattern):
                    return _p % frame

            # assemble the playback sequence as symlinks (handles loop/bounce
            # ordering and range without duplicating pixels on disk)
            index = 0
            for frame in _playback_order(first, last, playback):
                src = source_for(frame)
                if not os.path.isfile(src):
                    continue
                index += 1
                os.symlink(src, os.path.join(seq_dir, "seq.%05d%s" % (index, src_ext)))
            if index == 0:
                raise RuntimeError(
                    "no frames found to encode (looked for {})".format(source_for(first)))
            _log("  {} frames queued, encoding with ffmpeg".format(index))

            sequence_glob = os.path.join(seq_dir, "seq.*" + src_ext)
            palette_path = os.path.join(work_dir, "palette.png")
            _run_ffmpeg(sequence_glob, palette_path, output_path, fps_value, ffmpeg)
            _log("  wrote {}".format(output_path))
            created_paths.append(output_path)

            # keep the generated frames if asked (only meaningful when we rendered)
            if keep and rendered_dir is not None:
                kept = os.path.join(output_dir, "{}_frames".format(_safe_name(node.fullName())))
                shutil.rmtree(kept, ignore_errors=True)
                shutil.move(rendered_dir, kept)
                kept_dirs.append(kept)
                rendered_dir = None

            # read the finished GIF back into the script (below the source node)
            read_node = nuke.nodes.Read()
            read_node["file"].fromUserText(output_path)
            read_node.setXYpos(node.xpos(), node.ypos() + node.screenHeight() * 3)
            new_reads.append(read_node)

        except Exception as exc:
            _log("  FAILED: {}".format(exc))
            # ffmpeg errors arrive as CalledProcessError with the real reason on
            # .stderr; str(exc) alone drops it, so pull it out explicitly
            detail = getattr(exc, "stderr", None)
            if detail:
                _log("  ffmpeg stderr:\n{}".format(detail.strip()))
            failed_nodes.append(node.fullName())
        finally:
            if write_node is not None:
                nuke.delete(write_node)
            shutil.rmtree(work_dir, ignore_errors=True)

    # the new Read nodes are the on-success confirmation, so only pop up when
    # something needs attention (nothing created, or some nodes failed)
    if not created_paths:
        nuke.message("No GIFs were created. Check Script Editor for details.")
    elif failed_nodes:
        message = "Created {} GIF(s) in:\n{}".format(len(created_paths), output_dir)
        if kept_dirs:
            message += "\n\nKept frames:\n{}".format("\n".join(kept_dirs))
        message += "\n\nFailed:\n{}".format("\n".join(failed_nodes))
        message += "\n\nCheck Script Editor for details."
        nuke.message(message)

    return created_paths
