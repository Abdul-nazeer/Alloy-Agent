# Contributing to Alloy-Agent

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository
```bash
git clone https://github.com/Abdul-nazeer/Alloy-Agent.git
cd Alloy-Agent
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks
```bash
pre-commit install
```

## Code Quality Standards

- **Black** for code formatting (120 char line length)
- **isort** for import sorting
- **flake8** for linting
- **Type hints** where applicable
- **Docstrings** for all public functions/classes

## Running Tests

```bash
pytest tests/
```

## Pull Request Process

1. Create a feature branch from `develop`
2. Make your changes
3. Run code quality checks: `pre-commit run --all-files`
4. Run tests: `pytest`
5. Update documentation if needed
6. Submit PR to `develop` branch

## Code Review Criteria

- ✅ All tests pass
- ✅ Code quality checks pass
- ✅ Documentation updated
- ✅ No breaking changes without discussion
- ✅ Clean commit history

## Questions?

Open an issue or reach out to maintainers.
