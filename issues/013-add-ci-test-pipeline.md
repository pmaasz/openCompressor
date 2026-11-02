# Issue 013: Add CI/CD test pipeline

**Type:** Infrastructure - P1  
**Component:** CI  
**Labels:** ci, P1

## Description
No CI configuration visible (.github/workflows missing). Need automated testing on push/PR.

## Suggested Approach
Create GitHub Actions workflow:
- Run on push to main/develop, PRs
- Set up Python environment
- Install dependencies (with system deps for PyQt5 if needed)
- Run tests with xvfb for headless GUI tests
- Run linting (flake8/black/ruff)
- Generate coverage report
- Upload artifacts

## Example Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install deps
        run: |
          sudo apt-get update
          sudo apt-get install -y xvfb libxcb-xinerama0 ...
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-qt
      - name: Run tests
        run: xvfb-run -a python -m pytest tests/ -v --cov=src
```

## Acceptance Criteria
- [ ] GitHub Actions workflow added
- [ ] Tests run on PRs and pushes
- [ ] Linting passes
- [ ] Coverage reported
