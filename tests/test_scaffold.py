"""Tests for the scaffold engine."""

import os
import tempfile

import pytest

from scaffoldcraft.models import StructureNode
from scaffoldcraft.scaffold import scaffold, ScaffoldResult
from scaffoldcraft.parsers.tree import parse_tree
from scaffoldcraft.parsers.json_spec import parse_json


def _simple_nodes():
    """Build a simple tree manually for testing."""
    root = StructureNode("my-app", is_dir=True)
    src  = StructureNode("src", is_dir=True)
    src.add_child(StructureNode("main.py", content="# main\n"))
    src.add_child(StructureNode("utils.py", content=""))
    root.add_child(src)
    root.add_child(StructureNode("README.md", content="# My App\n"))
    return [root]


class TestScaffold:
    def test_creates_directories(self):
        with tempfile.TemporaryDirectory() as d:
            result = scaffold(_simple_nodes(), output_dir=d, verbose=False)
            assert os.path.isdir(os.path.join(d, "my-app", "src"))

    def test_creates_files(self):
        with tempfile.TemporaryDirectory() as d:
            scaffold(_simple_nodes(), output_dir=d, verbose=False)
            assert os.path.isfile(os.path.join(d, "my-app", "src", "main.py"))
            assert os.path.isfile(os.path.join(d, "my-app", "README.md"))

    def test_file_content_written(self):
        with tempfile.TemporaryDirectory() as d:
            scaffold(_simple_nodes(), output_dir=d, verbose=False)
            content = open(os.path.join(d, "my-app", "src", "main.py")).read()
            assert content == "# main\n"

    def test_empty_file_created(self):
        with tempfile.TemporaryDirectory() as d:
            scaffold(_simple_nodes(), output_dir=d, verbose=False)
            path = os.path.join(d, "my-app", "src", "utils.py")
            assert os.path.isfile(path)
            assert open(path).read() == ""

    def test_dry_run_no_files_created(self):
        with tempfile.TemporaryDirectory() as d:
            result = scaffold(_simple_nodes(), output_dir=d, dry_run=True, verbose=False)
            assert result.dry_run is True
            assert not os.path.exists(os.path.join(d, "my-app"))

    def test_dry_run_result_counts(self):
        with tempfile.TemporaryDirectory() as d:
            result = scaffold(_simple_nodes(), output_dir=d, dry_run=True, verbose=False)
            assert result.total_created > 0

    def test_skip_existing_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            scaffold(_simple_nodes(), output_dir=d, verbose=False)
            # Write different content to a file
            path = os.path.join(d, "my-app", "README.md")
            open(path, "w").write("CHANGED\n")
            # Second scaffold should skip it
            result = scaffold(_simple_nodes(), output_dir=d, verbose=False)
            assert path in result.skipped
            assert open(path).read() == "CHANGED\n"

    def test_overwrite_replaces_file(self):
        with tempfile.TemporaryDirectory() as d:
            scaffold(_simple_nodes(), output_dir=d, verbose=False)
            path = os.path.join(d, "my-app", "README.md")
            open(path, "w").write("CHANGED\n")
            scaffold(_simple_nodes(), output_dir=d, overwrite=True, verbose=False)
            assert open(path).read() == "# My App\n"

    def test_result_success_true(self):
        with tempfile.TemporaryDirectory() as d:
            result = scaffold(_simple_nodes(), output_dir=d, verbose=False)
            assert result.success is True

    def test_result_counts(self):
        with tempfile.TemporaryDirectory() as d:
            result = scaffold(_simple_nodes(), output_dir=d, verbose=False)
            assert len(result.created_dirs) >= 2   # my-app, src
            assert len(result.created_files) >= 3  # main.py, utils.py, README.md

    def test_empty_nodes_list(self):
        with tempfile.TemporaryDirectory() as d:
            result = scaffold([], output_dir=d, verbose=False)
            assert result.total_created == 0

    def test_from_tree_string(self):
        tree = "project/\n├── a.py\n└── b.py\n"
        nodes = parse_tree(tree)
        with tempfile.TemporaryDirectory() as d:
            result = scaffold(nodes, output_dir=d, verbose=False)
            assert os.path.isfile(os.path.join(d, "project", "a.py"))
            assert os.path.isfile(os.path.join(d, "project", "b.py"))

    def test_from_json_spec(self):
        spec = {"api/": {"main.py": "# api\n", "models.py": None}}
        nodes = parse_json(spec)
        with tempfile.TemporaryDirectory() as d:
            scaffold(nodes, output_dir=d, verbose=False)
            assert os.path.isfile(os.path.join(d, "api", "main.py"))
            content = open(os.path.join(d, "api", "main.py")).read()
            assert content == "# api\n"
