"""
Template variable substitution for scaffold-craft.

Supports placeholders like {{project_name}}, {{author}}, {{year}}
that get replaced at scaffold time.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, List, Optional

from scaffoldcraft.models import StructureNode

# Pattern to match {{variable_name}}
_VAR_PATTERN = re.compile(r"\{\{(\w+)\}\}")


def apply_variables(node: StructureNode, variables: Optional[Dict[str, str]] = None) -> None:
    """Recursively apply template variable substitution to a node tree.

    Replaces {{variable_name}} placeholders in node names and file contents.
    Also provides built-in variables: {{year}} (current year).

    Parameters
    ----------
    node:
        The root node to process (modified in-place).
    variables:
        Dictionary of variable name → replacement value.
    """
    if variables is None:
        variables = {}

    # Add built-in variables
    vars_with_builtins = dict(variables)
    if "year" not in vars_with_builtins:
        vars_with_builtins["year"] = str(datetime.now().year)

    # Apply to node name
    node.name = _substitute(node.name, vars_with_builtins)

    # Apply to file content
    if node.content is not None:
        node.content = _substitute(node.content, vars_with_builtins)

    # Recurse into children
    for child in node.children:
        apply_variables(child, variables)


def _substitute(text: str, variables: Dict[str, str]) -> str:
    """Replace all {{var}} placeholders in text."""
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        if var_name in variables:
            return variables[var_name]
        return match.group(0)  # Leave unknown variables as-is

    return _VAR_PATTERN.sub(replacer, text)
