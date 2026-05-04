"""
Tree-string parser.

Parses the ASCII/Unicode tree format that appears in READMEs and
documentation — the kind produced by the ``tree`` command or written
by hand::

    my-app/
    ├── src/
    │   ├── components/
    │   │   └── Button.tsx
    │   └── App.tsx
    ├── tests/
    │   └── App.test.tsx
    ├── package.json
    └── README.md

Rules
-----
- Lines ending with ``/`` are directories.
- All other lines are files.
- Indentation (via ``│``, ``├──``, ``└──``, spaces, or tabs) determines
  the parent-child relationship.
- Inline comments after ``#`` are captured in ``StructureNode.comment``.
- Blank lines and lines containing only box-drawing characters are skipped.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from scaffoldcraft.models import StructureNode

# Box-drawing characters used in tree output
_TREE_CHARS = set("│├└─ \t")

# Regex to strip tree prefix characters and capture the name
_STRIP_PREFIX = re.compile(r"^[│├└─\s]+")

# Characters that indicate a line is purely decorative
_DECORATIVE = re.compile(r"^[│\s]*$")


def _strip_tree_prefix(line: str) -> Tuple[str, int]:
    """Remove tree-drawing prefix and return (clean_name, indent_level).

    The indent level is the number of 4-character groups in the prefix,
    which corresponds to the depth in the tree.

    Parameters
    ----------
    line:
        Raw line from the tree string.

    Returns
    -------
    tuple
        ``(name, depth)`` where *name* is the cleaned node name and
        *depth* is the 0-indexed nesting level.
    """
    # Count leading spaces/tabs/box chars to determine depth
    prefix_match = _STRIP_PREFIX.match(line)
    prefix = prefix_match.group(0) if prefix_match else ""

    # Each level of nesting adds 4 characters (│   or ├── or └── )
    # Count the number of "│" or "    " groups
    depth = 0
    i = 0
    while i < len(prefix):
        if prefix[i] in ("│", "├", "└"):
            depth += 1
            i += 4  # skip "│   " or "├── " or "└── "
        elif prefix[i] in (" ", "\t"):
            # Plain indentation (4 spaces or 1 tab = 1 level)
            spaces = 0
            while i < len(prefix) and prefix[i] in (" ", "\t"):
                spaces += 1
                i += 1
            depth += spaces // 4
        else:
            i += 1

    name = line[len(prefix):].strip()
    return name, depth


def _parse_name_and_comment(raw: str) -> Tuple[str, str]:
    """Split a raw name into (name, comment).

    Inline comments start with ``#`` and are separated from the name
    by at least one space.

    Parameters
    ----------
    raw:
        Raw name string, possibly containing an inline comment.

    Returns
    -------
    tuple
        ``(name, comment)`` strings.
    """
    if "  #" in raw:
        parts = raw.split("  #", 1)
        return parts[0].strip(), parts[1].strip()
    if " # " in raw:
        parts = raw.split(" # ", 1)
        return parts[0].strip(), parts[1].strip()
    return raw.strip(), ""


def parse_tree(text: str) -> List[StructureNode]:
    """Parse a tree-style text string into a list of root :class:`~scaffoldcraft.models.StructureNode` objects.

    Parameters
    ----------
    text:
        Multi-line tree string (as produced by the ``tree`` command or
        written by hand in README files).

    Returns
    -------
    List[StructureNode]
        Top-level nodes.  Usually a single root directory, but may be
        multiple if the input has no common root.

    Examples
    --------
    >>> nodes = parse_tree('''
    ... my-app/
    ... ├── src/
    ... │   └── main.py
    ... └── README.md
    ... ''')
    >>> nodes[0].name
    'my-app'
    """
    lines = text.splitlines()
    roots: List[StructureNode] = []
    # Stack of (depth, node) pairs
    stack: List[Tuple[int, StructureNode]] = []

    for raw_line in lines:
        # Skip blank lines and purely decorative lines
        if not raw_line.strip():
            continue
        if _DECORATIVE.match(raw_line):
            continue

        name_raw, depth = _strip_tree_prefix(raw_line)
        if not name_raw:
            continue

        name, comment = _parse_name_and_comment(name_raw)
        if not name:
            continue

        is_dir = name.endswith("/")
        if is_dir:
            name = name.rstrip("/")

        node = StructureNode(name=name, is_dir=is_dir, comment=comment)

        if depth == 0:
            roots.append(node)
            stack = [(0, node)]
        else:
            # Pop stack until we find the parent at depth - 1
            while stack and stack[-1][0] >= depth:
                stack.pop()

            if stack:
                parent = stack[-1][1]
                parent.add_child(node)
            else:
                # Orphan node — attach to last root
                if roots:
                    roots[-1].add_child(node)
                else:
                    roots.append(node)

            stack.append((depth, node))

    return roots
