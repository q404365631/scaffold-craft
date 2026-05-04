"""
Scaffolder — creates files and directories on disk from a StructureNode tree.

This is the core engine.  It takes the IR produced by any parser and
materialises it as real files and folders.  It is intentionally kept
simple and parser-agnostic.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

from scaffoldcraft.models import StructureNode

_GREEN  = "\033[92m"
_CYAN   = "\033[96m"
_YELLOW = "\033[93m"
_DIM    = "\033[2m"
_RESET  = "\033[0m"


@dataclass
class ScaffoldResult:
    """Result of a scaffold operation.

    Attributes
    ----------
    created_dirs:
        Paths of directories that were created.
    created_files:
        Paths of files that were created.
    skipped:
        Paths that were skipped because they already existed.
    errors:
        Error messages for any paths that could not be created.
    dry_run:
        Whether this was a dry-run (nothing written to disk).
    """

    created_dirs:  List[str] = field(default_factory=list)
    created_files: List[str] = field(default_factory=list)
    skipped:       List[str] = field(default_factory=list)
    errors:        List[str] = field(default_factory=list)
    dry_run:       bool = False

    @property
    def total_created(self) -> int:
        return len(self.created_dirs) + len(self.created_files)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def _walk(
    node: StructureNode,
    base: Path,
    result: ScaffoldResult,
    overwrite: bool,
    dry_run: bool,
    on_create: Optional[Callable[[str, str], None]],
) -> None:
    """Recursively create a node and its children.

    Parameters
    ----------
    node:
        The current node to process.
    base:
        The parent directory path on disk.
    result:
        The :class:`ScaffoldResult` to update.
    overwrite:
        If ``True``, overwrite existing files.
    dry_run:
        If ``True``, do not write anything to disk.
    on_create:
        Optional callback ``(path, kind)`` called for each created item.
        *kind* is ``"dir"`` or ``"file"``.
    """
    target = base / node.name

    if node.is_dir:
        if not dry_run:
            try:
                target.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                result.errors.append(f"Cannot create dir {target}: {exc}")
                return
        result.created_dirs.append(str(target))
        if on_create:
            on_create(str(target), "dir")
        for child in node.children:
            _walk(child, target, result, overwrite, dry_run, on_create)
    else:
        if target.exists() and not overwrite:
            result.skipped.append(str(target))
            return
        if not dry_run:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                content = node.content or ""
                target.write_text(content, encoding="utf-8")
            except OSError as exc:
                result.errors.append(f"Cannot create file {target}: {exc}")
                return
        result.created_files.append(str(target))
        if on_create:
            on_create(str(target), "file")


def scaffold(
    nodes: List[StructureNode],
    output_dir: str = ".",
    overwrite: bool = False,
    dry_run: bool = False,
    verbose: bool = True,
) -> ScaffoldResult:
    """Create the project structure on disk.

    Parameters
    ----------
    nodes:
        List of root :class:`~scaffoldcraft.models.StructureNode` objects
        (as returned by any parser).
    output_dir:
        Directory under which the structure will be created.
    overwrite:
        If ``True``, overwrite existing files.  Existing directories are
        always reused (never deleted).
    dry_run:
        If ``True``, print what would be created without touching the disk.
    verbose:
        Print progress to stderr.

    Returns
    -------
    ScaffoldResult
        Summary of what was created, skipped, and any errors.
    """
    base   = Path(output_dir).resolve()
    result = ScaffoldResult(dry_run=dry_run)
    use_color = sys.stderr.isatty()

    def _on_create(path: str, kind: str) -> None:
        if not verbose:
            return
        rel = Path(path).relative_to(base)
        if kind == "dir":
            c = _CYAN if use_color else ""
            r = _RESET if use_color else ""
            print(f"  {c}mkdir{r}  {rel}/", file=sys.stderr)
        else:
            g = _GREEN if use_color else ""
            r = _RESET if use_color else ""
            print(f"  {g}touch{r}  {rel}", file=sys.stderr)

    if verbose:
        mode = f"{_YELLOW}DRY RUN{_RESET}" if (dry_run and use_color) else ("DRY RUN" if dry_run else "LIVE")
        print(f"\n  scaffold-craft [{mode}]  →  {base}\n", file=sys.stderr)

    for node in nodes:
        _walk(node, base, result, overwrite, dry_run, _on_create)

    if verbose:
        print(file=sys.stderr)
        g = _GREEN if use_color else ""
        r = _RESET if use_color else ""
        print(
            f"  {g}Created:{r} {len(result.created_dirs)} dirs, "
            f"{len(result.created_files)} files  |  "
            f"Skipped: {len(result.skipped)}  |  "
            f"Errors: {len(result.errors)}",
            file=sys.stderr,
        )
        if result.errors:
            for err in result.errors:
                print(f"  Error: {err}", file=sys.stderr)
        print(file=sys.stderr)

    return result
