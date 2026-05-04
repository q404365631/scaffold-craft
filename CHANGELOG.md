# Changelog

All notable changes to scaffold-craft will be documented here.

## [1.0.0] — 2026-05-04

### Added
- Tree-string parser (README/`tree` command format)
- JSON spec parser with file content and inline comments
- YAML spec parser (requires `pyyaml` optional dependency)
- Core scaffold engine with dry-run, overwrite, and skip-existing
- CLI: `scaffold tree`, `scaffold json`, `scaffold yaml`, `scaffold example`
- `StructureNode` IR model with `all_paths()`, `find()`, `to_dict_rows()`
- 25 tests — all run with zero dependencies

### Roadmap
- v1.1: Image input via Ollama vision (llava) or OpenAI vision API
- v1.2: VS Code extension
- v1.3: Template variables (`{{project_name}}`, `{{author}}`, etc.)
- v2.0: AI-generated structures from plain-English descriptions
