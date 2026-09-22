# Contributing to PrintForge

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/printforge/printforge.git
   cd printforge
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   pytest tests/ -v
   ```

## Testing Requirements

- All new features and bug fixes must include tests.
- Tests must pass without physical hardware (use the simulator).
- Run `pytest tests/ -v` before submitting a pull request.
- Aim for meaningful coverage; avoid flaky tests.

## Code Style

- Follow PEP 8.
- Use type hints.
- Keep functions small and focused.
- Do not break API contracts without a version bump.

## Pull Requests

- Fork the repo and create a feature branch.
- Update documentation if you change public behavior.
- Ensure CI passes before requesting review.
