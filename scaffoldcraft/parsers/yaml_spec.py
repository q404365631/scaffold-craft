"""
YAML spec parser.

Parses a YAML specification into a :class:`~scaffoldcraft.models.StructureNode` tree.
Uses the same structure as the JSON spec — keys ending with ``/`` are
directories, all others are files.

Requires PyYAML::

    pip install "scaffold-craft[yaml]"

Falls back gracefully with a clear error message if PyYAML is not installed.

YAML spec example::

    my-app/:
      src/:
        main.py: "# Entry point\\n"
        utils.py: ~
      tests/:
        __init__.py: ~
        test_main.py: "import pytest\\n"
      README.md:
        content: "# My App"
        comment: "project readme"
      pyproject.toml: ~
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Union

from scaffoldcraft.models import StructureNode
from scaffoldcraft.parsers.json_spec import _parse_node


def parse_yaml(source: Union[str, dict]) -> List[StructureNode]:
    """Parse a YAML spec string or dict into a list of root nodes.

    Parameters
    ----------
    source:
        Either a YAML string or an already-parsed Python dict.

    Returns
    -------
    List[StructureNode]
        Top-level nodes from the spec.

    Raises
    ------
    ImportError
        If PyYAML is not installed.
    ValueError
        If *source* cannot be parsed as YAML.
    """
    if isinstance(source, dict):
        data = source
    else:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "PyYAML is required for YAML spec support.\n"
                "Install it with: pip install 'scaffold-craft[yaml]'"
            ) from exc
        try:
            data = yaml.safe_load(source)
        except Exception as exc:
            raise ValueError(f"Invalid YAML spec: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("YAML spec must be a top-level mapping.")

    return [_parse_node(name, value) for name, value in data.items()]


def parse_yaml_file(path: str) -> List[StructureNode]:
    """Load and parse a YAML spec file.

    Parameters
    ----------
    path:
        Path to the ``.yaml`` or ``.yml`` spec file.

    Returns
    -------
    List[StructureNode]
        Top-level nodes from the spec.
    """
    text = Path(path).read_text(encoding="utf-8")
    return parse_yaml(text)
