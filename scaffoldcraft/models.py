"""
Intermediate representation (IR) for a project structure.

All parsers (tree string, JSON, YAML, image) produce a tree of
:class:`StructureNode` objects.  The scaffolder consumes this IR to
create files and folders on disk.

Keeping the IR separate from the parsers means adding a new input
format only requires writing a new parser — the scaffolder stays
unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class StructureNode:
    """A single node in the project structure tree.

    A node is either a **directory** (``is_dir=True``) or a **file**
    (``is_dir=False``).  Files may carry optional stub content that
    will be written when the file is created.

    Attributes
    ----------
    name:
        File or directory name (not a full path).
    is_dir:
        ``True`` if this node represents a directory.
    children:
        Child nodes (only meaningful when ``is_dir=True``).
    content:
        Optional stub content to write into the file.
        ``None`` creates an empty file.
    comment:
        Optional inline comment from the source spec (e.g. ``# entry point``).
    """

    name: str
    is_dir: bool = False
    children: List["StructureNode"] = field(default_factory=list)
    content: Optional[str] = None
    comment: str = ""

    def add_child(self, node: "StructureNode") -> None:
        """Append *node* as a child of this directory node."""
        self.children.append(node)

    def find(self, name: str) -> Optional["StructureNode"]:
        """Return the first direct child with the given *name*, or ``None``."""
        for child in self.children:
            if child.name == name:
                return child
        return None

    def all_paths(self, base: str = "") -> List[str]:
        """Return all relative paths in this subtree.

        Parameters
        ----------
        base:
            Prefix to prepend to each path.

        Returns
        -------
        List[str]
            Relative paths for every node in the subtree.
        """
        current = f"{base}/{self.name}".lstrip("/") if base else self.name
        paths = [current]
        for child in self.children:
            paths.extend(child.all_paths(base=current))
        return paths

    def __repr__(self) -> str:
        kind = "dir" if self.is_dir else "file"
        return f"StructureNode({self.name!r}, {kind}, children={len(self.children)})"
