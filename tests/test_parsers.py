"""Tests for scaffold-craft parsers."""

import json
import pytest

from scaffoldcraft.models import StructureNode
from scaffoldcraft.parsers.tree import parse_tree, _strip_tree_prefix, _parse_name_and_comment
from scaffoldcraft.parsers.json_spec import parse_json


# ---------------------------------------------------------------------------
# Tree parser tests
# ---------------------------------------------------------------------------

SIMPLE_TREE = """\
my-app/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── README.md
"""

FLAT_TREE = """\
project/
├── a.py
├── b.py
└── c.py
"""

DEEP_TREE = """\
root/
├── level1/
│   ├── level2/
│   │   └── deep.txt
│   └── mid.txt
└── top.txt
"""

NO_ROOT_TREE = """\
├── a.py
└── b.py
"""


class TestTreeParser:
    def test_parses_root_directory(self):
        nodes = parse_tree(SIMPLE_TREE)
        assert len(nodes) == 1
        assert nodes[0].name == "my-app"
        assert nodes[0].is_dir is True

    def test_parses_children(self):
        nodes = parse_tree(SIMPLE_TREE)
        root = nodes[0]
        child_names = [c.name for c in root.children]
        assert "src" in child_names
        assert "tests" in child_names
        assert "README.md" in child_names

    def test_nested_children(self):
        nodes = parse_tree(SIMPLE_TREE)
        src = nodes[0].find("src")
        assert src is not None
        assert src.is_dir is True
        src_children = [c.name for c in src.children]
        assert "main.py" in src_children
        assert "utils.py" in src_children

    def test_files_are_not_dirs(self):
        nodes = parse_tree(SIMPLE_TREE)
        readme = nodes[0].find("README.md")
        assert readme is not None
        assert readme.is_dir is False

    def test_flat_structure(self):
        nodes = parse_tree(FLAT_TREE)
        root = nodes[0]
        assert len(root.children) == 3

    def test_deep_nesting(self):
        nodes = parse_tree(DEEP_TREE)
        level1 = nodes[0].find("level1")
        assert level1 is not None
        level2 = level1.find("level2")
        assert level2 is not None
        deep = level2.find("deep.txt")
        assert deep is not None

    def test_empty_input(self):
        nodes = parse_tree("")
        assert nodes == []

    def test_blank_lines_ignored(self):
        text = "\n\nmy-app/\n\n├── src/\n\n"
        nodes = parse_tree(text)
        assert len(nodes) == 1

    def test_inline_comment_captured(self):
        text = "project/\n└── main.py  # entry point\n"
        nodes = parse_tree(text)
        main = nodes[0].find("main.py")
        assert main is not None
        assert "entry point" in main.comment

    def test_all_paths(self):
        nodes = parse_tree(SIMPLE_TREE)
        paths = nodes[0].all_paths()
        assert "my-app/src/main.py" in paths
        assert "my-app/README.md" in paths

    def test_strip_tree_prefix_depth_zero(self):
        name, depth = _strip_tree_prefix("my-app/")
        assert depth == 0
        assert name == "my-app/"

    def test_parse_name_and_comment(self):
        name, comment = _parse_name_and_comment("main.py  # entry point")
        assert name == "main.py"
        assert comment == "entry point"

    def test_parse_name_no_comment(self):
        name, comment = _parse_name_and_comment("main.py")
        assert name == "main.py"
        assert comment == ""


# ---------------------------------------------------------------------------
# JSON spec parser tests
# ---------------------------------------------------------------------------

SIMPLE_JSON = {
    "my-api/": {
        "app/": {
            "__init__.py": None,
            "main.py": "from fastapi import FastAPI\n",
        },
        "README.md": None,
    }
}

FLAT_JSON = {
    "project/": {
        "a.py": None,
        "b.py": "# b module\n",
        "c.py": {"content": "# c module\n", "comment": "utility"},
    }
}


class TestJsonParser:
    def test_parses_root(self):
        nodes = parse_json(SIMPLE_JSON)
        assert len(nodes) == 1
        assert nodes[0].name == "my-api"
        assert nodes[0].is_dir is True

    def test_parses_nested_dirs(self):
        nodes = parse_json(SIMPLE_JSON)
        app = nodes[0].find("app")
        assert app is not None
        assert app.is_dir is True

    def test_parses_files(self):
        nodes = parse_json(SIMPLE_JSON)
        app = nodes[0].find("app")
        init = app.find("__init__.py")
        assert init is not None
        assert init.is_dir is False

    def test_file_content(self):
        nodes = parse_json(SIMPLE_JSON)
        app = nodes[0].find("app")
        main = app.find("main.py")
        assert main.content == "from fastapi import FastAPI\n"

    def test_null_content_is_empty_string(self):
        nodes = parse_json(SIMPLE_JSON)
        readme = nodes[0].find("README.md")
        assert readme.content == ""

    def test_dict_content_and_comment(self):
        nodes = parse_json(FLAT_JSON)
        c = nodes[0].find("c.py")
        assert c.content == "# c module\n"
        assert c.comment == "utility"

    def test_json_string_input(self):
        nodes = parse_json(json.dumps(SIMPLE_JSON))
        assert len(nodes) == 1

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_json("{not valid}")

    def test_non_dict_raises(self):
        with pytest.raises(ValueError):
            parse_json("[1, 2, 3]")

    def test_empty_dict(self):
        nodes = parse_json({})
        assert nodes == []
