"""
scaffold-craft
==============
Scaffold any project structure from a tree string, JSON spec, or YAML spec.

Roadmap
-------
- v1.0 (MVP)  : Tree string parser, JSON spec, YAML spec, CLI
- v1.1        : Image input via Ollama vision (llava) or OpenAI vision API
- v1.2        : VS Code extension
- v1.3        : Template variables ({{project_name}}, {{author}}, etc.)
- v2.0        : AI-generated structures from plain-English descriptions

Public API
----------
- :func:`~scaffoldcraft.parsers.tree.parse_tree`   — parse tree-style text
- :func:`~scaffoldcraft.parsers.json_spec.parse_json` — parse JSON spec
- :func:`~scaffoldcraft.scaffold.scaffold`          — create files on disk
- :class:`~scaffoldcraft.models.StructureNode`      — the IR node model
"""

__version__ = "1.0.0"
__author__  = "Jishanahmed AR Shaikh"
__license__ = "MIT"

from scaffoldcraft.models import StructureNode          # noqa: F401
from scaffoldcraft.scaffold import scaffold             # noqa: F401
from scaffoldcraft.parsers.tree import parse_tree       # noqa: F401
from scaffoldcraft.parsers.json_spec import parse_json  # noqa: F401
