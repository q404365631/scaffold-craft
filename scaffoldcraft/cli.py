"""
Command-line interface for scaffold-craft.

Usage
-----
    # From a tree string (pipe or file)
    scaffold tree --input structure.txt --output ./my-project
    echo "my-app/\\n├── src/\\n└── README.md" | scaffold tree

    # From a JSON spec
    scaffold json --input spec.json --output ./my-project

    # From a YAML spec
    scaffold yaml --input spec.yaml --output ./my-project

    # Dry run (preview without creating files)
    scaffold tree --input structure.txt --dry-run

    # Show a built-in example
    scaffold example
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scaffoldcraft import __version__
from scaffoldcraft.scaffold import scaffold

_EXAMPLE_TREE = """\
my-app/
├── src/
│   ├── components/
│   │   └── Button.tsx
│   ├── pages/
│   │   └── index.tsx
│   └── App.tsx
├── tests/
│   └── App.test.tsx
├── public/
│   └── favicon.ico
├── package.json
├── tsconfig.json
└── README.md
"""

_EXAMPLE_JSON = """\
{
  "my-api/": {
    "app/": {
      "__init__.py": null,
      "main.py": "from fastapi import FastAPI\\n\\napp = FastAPI()\\n",
      "models.py": null,
      "routes/": {
        "__init__.py": null,
        "users.py": null
      }
    },
    "tests/": {
      "__init__.py": null,
      "test_main.py": "import pytest\\n"
    },
    "requirements.txt": "fastapi\\nuvicorn\\n",
    "README.md": null
  }
}
"""


def _read_input(args: argparse.Namespace) -> str:
    """Read input from a file or stdin."""
    if hasattr(args, "input") and args.input:
        return Path(args.input).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("Error: provide --input FILE or pipe input via stdin.", file=sys.stderr)
    sys.exit(1)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="scaffold",
        description="Scaffold any project structure from a tree string, JSON spec, or YAML spec.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", "-V", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # Shared flags for all input commands
    def _add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--input",  "-i", metavar="FILE",
                       help="Input file (omit to read from stdin)")
        p.add_argument("--output", "-o", default=".",
                       metavar="DIR",
                       help="Output directory (default: current dir)")
        p.add_argument("--overwrite", action="store_true",
                       help="Overwrite existing files")
        p.add_argument("--dry-run",   action="store_true",
                       help="Preview without creating files")
        p.add_argument("--quiet", "-q", action="store_true",
                       help="Suppress progress output")

    # tree subcommand
    tree_p = sub.add_parser("tree", help="Scaffold from a tree-style text string")
    _add_common(tree_p)

    # json subcommand
    json_p = sub.add_parser("json", help="Scaffold from a JSON spec file")
    _add_common(json_p)

    # yaml subcommand
    yaml_p = sub.add_parser("yaml", help="Scaffold from a YAML spec file")
    _add_common(yaml_p)

    # example subcommand
    ex_p = sub.add_parser("example", help="Show built-in examples")
    ex_p.add_argument("--format", choices=["tree", "json"], default="tree",
                      help="Which example to show (default: tree)")
    ex_p.add_argument("--scaffold", action="store_true",
                      help="Actually scaffold the example into ./example-output/")

    args = parser.parse_args(argv)

    if args.command == "example":
        if args.format == "json":
            print(_EXAMPLE_JSON)
            if args.scaffold:
                from scaffoldcraft.parsers.json_spec import parse_json
                nodes = parse_json(_EXAMPLE_JSON)
                scaffold(nodes, output_dir="./example-output", verbose=True)
        else:
            print(_EXAMPLE_TREE)
            if args.scaffold:
                from scaffoldcraft.parsers.tree import parse_tree
                nodes = parse_tree(_EXAMPLE_TREE)
                scaffold(nodes, output_dir="./example-output", verbose=True)
        return

    if args.command == "tree":
        from scaffoldcraft.parsers.tree import parse_tree
        text  = _read_input(args)
        nodes = parse_tree(text)

    elif args.command == "json":
        from scaffoldcraft.parsers.json_spec import parse_json
        text  = _read_input(args)
        try:
            nodes = parse_json(text)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "yaml":
        from scaffoldcraft.parsers.yaml_spec import parse_yaml
        text = _read_input(args)
        try:
            nodes = parse_yaml(text)
        except (ImportError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        return

    if not nodes:
        print("Warning: no nodes parsed from input.", file=sys.stderr)
        sys.exit(0)

    result = scaffold(
        nodes,
        output_dir=args.output,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        verbose=not args.quiet,
    )

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
