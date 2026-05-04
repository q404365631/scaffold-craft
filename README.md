<div align="center">

# scaffold-craft

**Turn any project structure into real files and folders — instantly.**

Paste a tree from a README. Drop a JSON spec. Pipe from stdin. scaffold-craft reads it and builds the project on disk in seconds.

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Zero Runtime Deps](https://img.shields.io/badge/Runtime%20Deps-Zero-22c55e?style=flat)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat)](CONTRIBUTING.md)
[![CI](https://github.com/jishanahmed-shaikh/scaffold-craft/actions/workflows/ci.yml/badge.svg)](https://github.com/jishanahmed-shaikh/scaffold-craft/actions)

</div>

---

## The problem

You find a perfect project structure in a tutorial README. It looks like this:

```
my-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── models.py
├── tests/
│   └── test_main.py
└── requirements.txt
```

Now you manually create every folder and file one by one. That's 8 operations for a simple structure. For a real project it's 30+.

**scaffold-craft does it in one command.**

---

## Install

```bash
pip install scaffold-craft
```

Zero runtime dependencies. Works with Python 3.8+.

---

## Quick start

### From a tree string (copy from any README)

```bash
# Save the tree to a file
cat > structure.txt << 'EOF'
my-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── models.py
├── tests/
│   └── test_main.py
└── requirements.txt
EOF

# Scaffold it
scaffold tree --input structure.txt --output ./my-api
```

### From a JSON spec (with file content)

```json
{
  "my-api/": {
    "app/": {
      "__init__.py": null,
      "main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n",
      "models.py": null
    },
    "tests/": {
      "__init__.py": null,
      "test_main.py": "import pytest\n"
    },
    "requirements.txt": "fastapi\nuvicorn\n",
    "README.md": null
  }
}
```

```bash
scaffold json --input spec.json --output .
```

### From a YAML spec

```yaml
my-api/:
  app/:
    __init__.py: ~
    main.py: "from fastapi import FastAPI\n"
  tests/:
    test_main.py: "import pytest\n"
  requirements.txt: "fastapi\nuvicorn\n"
```

```bash
pip install "scaffold-craft[yaml]"
scaffold yaml --input spec.yaml --output .
```

### Pipe from stdin

```bash
echo "my-app/
├── src/
│   └── index.ts
└── package.json" | scaffold tree --output ./my-app
```

### Preview without creating files

```bash
scaffold tree --input structure.txt --dry-run
```

### See a built-in example

```bash
scaffold example           # print tree example
scaffold example --format json  # print JSON example
scaffold example --scaffold     # actually build the example
```

---

## Example output

```
  scaffold-craft [LIVE]  →  /home/user/projects

  mkdir  my-api/
  mkdir  my-api/app/
  touch  my-api/app/__init__.py
  touch  my-api/app/main.py
  touch  my-api/app/models.py
  mkdir  my-api/tests/
  touch  my-api/tests/__init__.py
  touch  my-api/tests/test_main.py
  touch  my-api/requirements.txt
  touch  my-api/README.md

  Created: 3 dirs, 7 files  |  Skipped: 0  |  Errors: 0
```

---

## All flags

| Flag | Description |
|------|-------------|
| `--input FILE` | Input file (omit to read from stdin) |
| `--output DIR` | Output directory (default: current dir) |
| `--overwrite` | Overwrite existing files |
| `--dry-run` | Preview without creating files |
| `--quiet` | Suppress progress output |

---

## Input formats

### Tree string

The format produced by the Unix `tree` command and used in most READMEs:

```
my-app/
├── src/
│   ├── components/
│   │   └── Button.tsx   # reusable button
│   └── App.tsx
└── package.json
```

- Lines ending with `/` are directories
- All other lines are files
- Inline comments after `#` are captured (not written to files)
- Works with `├──`, `└──`, `│`, plain spaces, or tabs

### JSON spec

```json
{
  "dir/": {
    "file.py": null,
    "file_with_content.py": "# content here\n",
    "file_with_comment.py": {
      "content": "# content\n",
      "comment": "entry point"
    }
  }
}
```

- Keys ending with `/` are directories
- `null` or `""` creates an empty file
- A string value is written as the file's content
- An object with `"content"` and `"comment"` keys is also supported

### YAML spec

Same structure as JSON, in YAML syntax. Requires `pip install "scaffold-craft[yaml]"`.

---

## Library usage

```python
from scaffoldcraft import parse_tree, parse_json, scaffold

# From a tree string
nodes = parse_tree("""
my-app/
├── src/
│   └── main.py
└── README.md
""")

# From a JSON spec
nodes = parse_json({
    "my-app/": {
        "src/": {"main.py": "# entry\n"},
        "README.md": None,
    }
})

# Scaffold to disk
result = scaffold(nodes, output_dir="./projects", dry_run=False)
print(f"Created {result.total_created} items")
print(f"Dirs:  {result.created_dirs}")
print(f"Files: {result.created_files}")
```

---

## Roadmap

| Version | Feature |
|---------|---------|
| **v1.0** | Tree string, JSON spec, YAML spec, CLI ✅ |
| **v1.1** | Image input — screenshot of VS Code file explorer via Ollama vision (llava) or OpenAI vision API |
| **v1.2** | VS Code extension — right-click → "Scaffold from structure" |
| **v1.3** | Template variables — `{{project_name}}`, `{{author}}`, `{{year}}` |
| **v2.0** | AI mode — describe in plain English, AI generates the structure |

---

## Project structure

```
scaffold-craft/
├── scaffoldcraft/
│   ├── __init__.py          # Public API
│   ├── models.py            # StructureNode IR
│   ├── scaffold.py          # Core engine (parser-agnostic)
│   ├── cli.py               # CLI: tree, json, yaml, example
│   └── parsers/
│       ├── tree.py          # Tree-string parser
│       ├── json_spec.py     # JSON spec parser
│       └── yaml_spec.py     # YAML spec parser (optional PyYAML)
├── tests/
│   ├── test_parsers.py      # 22 parser tests
│   └── test_scaffold.py     # 13 scaffold engine tests
└── pyproject.toml
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Adding a new input format (e.g. TOML, image) only requires writing a new parser that returns `List[StructureNode]` — the scaffold engine stays unchanged.

Issues labelled [`good first issue`](https://github.com/jishanahmed-shaikh/scaffold-craft/issues?q=label%3A%22good+first+issue%22) are a great place to start.

---

## License

[MIT](LICENSE) © 2026 [Jishanahmed AR Shaikh](https://github.com/jishanahmed-shaikh)
