"""
JSON spec parser.

Parses a structured JSON specification into a :class:`~scaffoldcraft.models.StructureNode` tree.

JSON spec format
----------------
The spec is a nested object where:

- A key ending with ``/`` is a directory.
- A key without ``/`` is a file.
- The value of a directory key is a nested object (its children).
- The value of a file key is either:
  - ``null`` / ``""``  — create an empty file
  - A string          — use as the file's stub content
  - An object with ``"content"`` and optional ``"comment"`` keys

Example::

    {
      "my-app/": {
        "src/": {
          "main.py": "# Entry point\\n",
          "utils.py": null
        },
        "tests/": {
          "__init__.py": null,
          "test_main.py": "import pytest\\n"
        },
        "README.md": {"content": "# My App", "comment": "project readme"},
        "pyproject.toml": null
      }
    }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union

from scaffoldcraft.models import StructureNode


def _parse_node(name: str, value: Any) -> StructureNode:
    """Recursively parse a single key-value pair into a :class:`~scaffoldcraft.models.StructureNode`.

    Parameters
    ----------
    name:
        The key from the JSON object (may end with ``/`` for directories).
    value:
        The value associated with the key.

    Returns
    -------
    StructureNode
        The parsed node with children populated for directories.
    """
    is_dir = name.endswith("/")
    clean_name = name.rstrip("/")

    if is_dir:
        node = StructureNode(name=clean_name, is_dir=True)
        if isinstance(value, dict):
            for child_name, child_value in value.items():
                node.add_child(_parse_node(child_name, child_value))
        return node

    # File node
    content: str = ""
    comment: str = ""

    if value is None or value == "":
        content = ""
    elif isinstance(value, str):
        content = value
    elif isinstance(value, dict):
        content = value.get("content", "") or ""
        comment = value.get("comment", "") or ""

    return StructureNode(name=clean_name, is_dir=False, content=content, comment=comment)


def parse_json(source: Union[str, dict]) -> List[StructureNode]:
    """Parse a JSON spec string or dict into a list of root nodes.

    Parameters
    ----------
    source:
        Either a JSON string or an already-parsed Python dict.

    Returns
    -------
    List[StructureNode]
        Top-level nodes from the spec.

    Raises
    ------
    ValueError
        If *source* is a string that cannot be parsed as JSON.
    TypeError
        If *source* is neither a string nor a dict.
    """
    if isinstance(source, str):
        try:
            data = json.loads(source)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON spec: {exc}") from exc
    elif isinstance(source, dict):
        data = source
    else:
        raise TypeError(f"Expected str or dict, got {type(source).__name__}")

    if not isinstance(data, dict):
        raise ValueError("JSON spec must be a top-level object (dict).")

    return [_parse_node(name, value) for name, value in data.items()]


def parse_json_file(path: str) -> List[StructureNode]:
    """Load and parse a JSON spec file.

    Parameters
    ----------
    path:
        Path to the ``.json`` spec file.

    Returns
    -------
    List[StructureNode]
        Top-level nodes from the spec.
    """
    text = Path(path).read_text(encoding="utf-8")
    return parse_json(text)
