# recursive_read_sd.py — Layout and directory-structure plan

## Part 1: Research (what happens now)

### Data flow

1. **Entry**: User picks one or more root folders (or path is taken from selected nodes’ file knobs). `walkPaths` is normalized to a list of directory paths.
2. **Collection**: `process_dir(walkPath, files=[], depth=0)` recursively walks each root and appends every file path to a **single flat list** `files`. Directory structure is not preserved—only the list of file paths is returned.
3. **Grouping**: The flat list is then grouped for backdrops:
  - `hcf` = highest common path (dirname of the common prefix of all `files`).
  - Files are sorted, then grouped with `itertools.groupby` using:
    - `sortDiscrete = lambda filepath: os.path.dirname(filepath.split(hcf)[1]).split('/')[1]`
  - So the group key is the **second path segment** of the path relative to `hcf` (e.g. for `hcf/seq/shot/plate/file.exr` the key is `shot`, not `seq/shot/plate`). Only one level of grouping is used.
4. **Node creation**: For each file, `nuke_loader(filepath)` creates the right node type (Read, StickyNote, Camera2, ReadGeo2, etc.). New nodes get Nuke’s default positions (often overlapping or scattered).
5. **Layout**: For each group:
  - `backdrop_sd.make_backdrop(nodes, label=uniquekeys[j])` creates a backdrop around those nodes (backdrop is sized to the current node positions).
  - All nodes and the backdrop are then shifted vertically: `y += j*20*gh` so groups stack one below the other.
  - There is **no layout of nodes inside** each group. The call to `arrange_by_sd.arrange_by(...)` that would lay nodes out in a grid is commented out (around 369–374 and 490–497).

### Why things end up “all over the place”

- **Flat list**: We never associate each file with its full directory path for layout, so we can’t place by folder hierarchy.
- **Shallow grouping**: Grouping by only the second path component (e.g. `split('/')[1]`) means:
  - Different branches with the same folder name (e.g. `proj/shotA/plate` and `proj/shotB/plate`) are merged into one backdrop.
  - Nested structure (e.g. `seq/shot/plate/v001`) is collapsed to one level; we don’t get “folder within folder” in the DAG.
- **No in-group layout**: Nodes in each backdrop keep their default positions, so they overlap or scatter. Only the backdrops are offset vertically.
- **Fragile key**: If the relative path has fewer than two segments (e.g. files directly under `hcf`), `split('/')[1]` can raise `IndexError`. Empty or single-segment keys can also produce odd groups.

### Other issues observed

- **Depth in `process_dir`**: `depth` is incremented before the recursive call (`depth += 1` then `process_dir(..., depth=depth)`). So when returning to a sibling directory, `depth` is already raised and can prevent further descent (e.g. with `maxdepth=1`, only the first subdir is followed). Intended behaviour is usually “depth passed as `depth+1`” without mutating the current `depth`.
- **Progress bar**: Progress uses `len(walkPath)` (length of the path string) instead of something like `len(walkPaths)` or number of files, so the bar doesn’t reflect real progress.

---

## Part 2: Design (expected behaviour and plan)

### Expected behaviour

1. **Respect directory structure**: Treat the tree of directories as the main organising principle. Each directory (or each “folder” level we care about) should map to a clear unit in the script (e.g. one backdrop per directory, or nested backdrops for nested folders).
2. **Read nodes in nested folders**: Files in subfolders should still be loaded, but their **placement** should reflect where they live:
  - One backdrop per directory; backdrops are arranged so that parent/child relationship is visible (e.g. parent folder’s backdrop contains child folder backdrops).
3. **Stable, readable layout**: Within each backdrop, nodes should be laid out in a line left to right so they don’t overlap and are easy to follow. Different nodetypes should be on different lines, i.e. you see a line of Read nodes left-to-right, then a line of Camera nodes left to right on a backdrop to represent that directory. Between backdrops, arrangement should be consistent (left-to-right for files, top-to-bottom by path).

### Plan (how to get there)

1. **Preserve structure when collecting files**
  - Change the collector so we keep **directory context** for each file. For example:
    - Either: build a small tree `(dirpath, list_of_files, list_of_subdir_trees)` and flatten later when creating nodes, or
    - Or: collect `(filepath, relative_dir_path)` where `relative_dir_path` is the path relative to the walk root (e.g. `seq/shot/plate`).
  - Use this to group by **full relative directory path** (or by a configurable depth of path), not by a single segment. That way “same name, different branch” stay in separate backdrops and nesting is visible.
2. **Fix grouping and keys**
  - Replace the current `sortDiscrete` with a key that uses the **full relative directory** (e.g. `os.path.relpath(os.path.dirname(filepath), walkPath)` or the equivalent from your structure).
  - Normalise path separators and handle edge cases: files directly under the root (relative dir `''` or `'.'`), and avoid `split('/')[1]` so there’s no IndexError. Decide how to label/group the root (e.g. “.” or “(root)”).
3. **Layout within each backdrop**
  - Lay out nodes **by node type, then left-to-right**: one row of Read nodes (left-to-right), then a row of Camera nodes (left-to-right), then ReadGeo, StickyNote, etc. So each backdrop shows that directory as “type by type, files in order.” Use `arrange_by_sd.arrange_by(nodes, sortKey=node class, sortDiscrete=True, ...)` or a small helper that groups by `node.Class()` and arranges each group in a horizontal line, stacking rows. Do this **before** creating the backdrop so `make_backdrop` fits a tidy block.
4. **Arrange backdrops by directory order**
  - Use **natural sort** for all ordering by path or filename (so e.g. `shot2`, `shot10`, `shot100` and path segments like `v001` sort numerically). Sort groups by the full relative directory path; order on the canvas matches the directory tree. Place backdrops top-to-bottom by path so hierarchy is easy to read.
5. **Nested backdrops (parent contains child) — two-pass layout**
  - Use a **two-pass layout** (agreed approach): (1) create all nodes and backdrops per directory, layout nodes within each backdrop; (2) compute bounding box of each backdrop, reposition child backdrops inside parent bounds, and expand parent backdrop size to fit.
  - Each directory gets one backdrop. **Child-directory backdrops must be placed inside the parent’s backdrop** so the DAG shows “folder inside folder.” Approach:
    - Build the directory tree when collecting files (step 1). When creating backdrops, process in **depth order** (e.g. breadth-first or depth-first) so parent bounds exist before placing children.
    - Pass 1: For each directory (in natural-sort order by relative path), create and layout its nodes (step 3), then create its backdrop at a provisional position.
    - Pass 2: For each parent directory, compute the bounding box of all its child backdrops; position those children inside the parent (offset from parent’s top-left, with padding); resize the parent backdrop so it fully contains all children. Sibling backdrops ordered by **natural sort** on relative path (e.g. left-to-right or top-to-bottom).
    - Ensure child backdrops don’t overlap each other and stay inside the parent.
6. **Clean-ups**
  - Fix `process_dir` depth: pass `depth + 1` into the recursive call and do not mutate `depth` (so siblings are processed at the same depth).
  - Fix progress reporting to use number of walk roots or number of files/dirs processed, not `len(walkPath)`.

Implementing steps 1–6 gives: nested folders as nested backdrops, nodes laid out by type (rows) within each backdrop, and directory order (top-to-bottom by path) between backdrops.