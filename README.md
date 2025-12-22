# Python integration for Mixpanel

This repository provides a comprehensive layer on top of the
[official Python library from Mixpanel](https://pypi.org/project/mixpanel/)
which adds:

* Support for anonymizing email addresses and including them in trakced events
* Django middleware & view support

## Development

It is recommended to use `uv` to develop locally.

### Testing (pytest)

Run the tests:

```bash
$ uv run pytest
```

### Type checking (mypy)

Run the type checker:

```bash
uv tool run mypy .
```

### Formatting and linting (ruff)

Run the formatter:

```bash
uv tool run ruff format
```

Run the linter:

```bash
uv tool run ruff check --fix
```
