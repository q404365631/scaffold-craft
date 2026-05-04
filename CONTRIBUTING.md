# Contributing to scaffold-craft

Contributions are very welcome. This project is designed to be extended — adding a new input format is as simple as writing a new parser that returns `List[StructureNode]`.

## Development setup

```bash
git clone https://github.com/jishanahmed-shaikh/scaffold-craft.git
cd scaffold-craft
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Adding a new parser

1. Create `scaffoldcraft/parsers/your_format.py`
2. Implement `parse_your_format(source) -> List[StructureNode]`
3. Add it to `scaffoldcraft/__init__.py` exports
4. Add a subcommand in `scaffoldcraft/cli.py`
5. Add tests in `tests/`

## Good first issues

See the [issue tracker](https://github.com/jishanahmed-shaikh/scaffold-craft/issues) for issues labelled `good first issue`.
