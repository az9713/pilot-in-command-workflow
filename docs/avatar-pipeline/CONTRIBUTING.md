# Contributing to Avatar Pipeline

Thank you for your interest in contributing to Avatar Pipeline! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)

## Code of Conduct

This project follows a code of conduct. By participating, you agree to:
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Ways to Contribute

- **Bug Reports**: Found a bug? Open an issue with details
- **Feature Requests**: Have an idea? Discuss it in an issue first
- **Code Contributions**: Fix bugs or implement features
- **Documentation**: Improve docs, examples, or guides
- **Testing**: Write tests or test on different hardware
- **Community**: Help others in issues and discussions

### Before You Start

1. **Check existing issues**: Someone may already be working on it
2. **Discuss major changes**: Open an issue to discuss before coding
3. **Start small**: First contribution? Try a "good first issue"

## Development Setup

### Prerequisites

- Python 3.10 or 3.11
- NVIDIA GPU with CUDA (for testing GPU features)
- Git

### Setup Steps

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/avatar-pipeline.git
cd avatar-pipeline

# 3. Add upstream remote
git remote add upstream https://github.com/avatar-pipeline/avatar-pipeline.git

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install in development mode with dev dependencies
pip install -e ".[dev]"

# 6. Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install

# 7. Verify installation
avatar status
pytest tests/
```

### Development Dependencies

The `[dev]` extra includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reports
- `black` - Code formatter
- `ruff` - Linter
- `mypy` - Type checker

## Development Workflow

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature
# Or for bug fixes: git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code following our style guide
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_voice.py

# Run with coverage
pytest --cov=src --cov-report=html

# Check formatting
black --check src/

# Run linter
ruff check src/

# Type checking
mypy src/
```

### 4. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of feature"
```

**Commit Message Format:**
```
<type>: <short summary>

<optional longer description>

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add support for custom voice models

fix: Resolve CUDA out of memory in sequential loading

docs: Update installation instructions for Windows

test: Add integration tests for pipeline coordinator
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/my-feature

# Then create Pull Request on GitHub
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Line length: 88 characters (Black default)
# Use Black for formatting
# Use type hints for function signatures

# Good example:
def process_audio(
    audio_path: Path,
    sample_rate: int = 16000,
    normalize: bool = True,
) -> np.ndarray:
    """
    Process audio file and return numpy array.

    Args:
        audio_path: Path to audio file
        sample_rate: Target sample rate in Hz
        normalize: Whether to normalize amplitude

    Returns:
        Processed audio as numpy array

    Raises:
        FileNotFoundError: If audio file doesn't exist
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    # Implementation
    pass
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import Optional, List, Dict, Any
from pathlib import Path

def good_function(
    text: str,
    profile_id: str,
    options: Optional[Dict[str, Any]] = None,
) -> List[Path]:
    """Function with proper type hints."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Short one-line description.

    Longer description if needed. Explain what the function does,
    not how it does it (that's what code is for).

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
        RuntimeError: When processing fails

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

### File Organization

```python
"""
Module docstring explaining the module's purpose.
"""

# 1. Standard library imports
import os
import sys
from pathlib import Path
from typing import Optional

# 2. Third-party imports
import torch
import numpy as np

# 3. Local imports
from ..config import load_config
from ..utils import VRAMManager

# 4. Constants
DEFAULT_SAMPLE_RATE = 16000
MAX_DURATION_SECONDS = 300

# 5. Main code
class MyClass:
    """Class docstring."""
    pass


def my_function():
    """Function docstring."""
    pass
```

### Naming Conventions

- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `lowercase_with_underscores()`
- **Variables**: `lowercase_with_underscores`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Private**: `_leading_underscore`

## Testing

### Writing Tests

Create tests in `tests/` directory:

```python
# tests/test_voice.py
import pytest
from pathlib import Path
from src.voice import XTTSVoiceCloner


class TestXTTSVoiceCloner:
    """Tests for XTTS voice cloner."""

    def test_init(self):
        """Test cloner initialization."""
        cloner = XTTSVoiceCloner(config={})
        assert cloner is not None

    def test_clone_voice_invalid_path(self):
        """Test error handling for invalid audio path."""
        cloner = XTTSVoiceCloner(config={})
        with pytest.raises(FileNotFoundError):
            cloner.clone_voice(Path("nonexistent.wav"), "test", "en")

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required")
    def test_clone_voice_gpu(self):
        """Test voice cloning on GPU."""
        # GPU-specific test
        pass
```

### Test Categories

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **System tests**: Test complete workflows
- **GPU tests**: Marked with `@pytest.mark.gpu`

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_voice.py

# Specific test
pytest tests/test_voice.py::TestXTTSVoiceCloner::test_init

# Skip GPU tests (if no GPU)
pytest -m "not gpu"

# With coverage
pytest --cov=src --cov-report=html
```

## Documentation

### Code Documentation

- All public functions must have docstrings
- Complex logic should have inline comments
- Update docstrings when changing function signatures

### User Documentation

- Update `README.md` for user-facing changes
- Add examples for new features
- Update configuration docs for new options

### API Documentation

API changes require:
- Docstring updates
- OpenAPI schema updates (for REST API)
- Example updates

## Submitting Changes

### Pull Request Process

1. **Ensure tests pass**: All tests must pass
2. **Update documentation**: Docs reflect changes
3. **Follow style guide**: Code is formatted and linted
4. **Write clear PR description**: Explain what and why

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Tested on GPU
- [ ] Tested on CPU

## Checklist
- [ ] Code follows style guide
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Fixes #123
```

### Review Checklist

Before submitting, verify:
- [ ] Tests pass: `pytest`
- [ ] Code formatted: `black src/`
- [ ] Linting passes: `ruff check src/`
- [ ] Type hints correct: `mypy src/`
- [ ] Documentation updated
- [ ] Examples work
- [ ] Commit messages clear
- [ ] Branch is up to date with main

## Review Process

### What to Expect

1. **Automated checks**: CI runs tests and linting
2. **Maintainer review**: Code review within 2-3 days
3. **Feedback**: Suggestions for improvements
4. **Iteration**: Make requested changes
5. **Approval**: Once all checks pass and review is positive
6. **Merge**: Maintainer merges PR

### Review Criteria

Reviewers check for:
- Correctness: Does it work as intended?
- Tests: Are there adequate tests?
- Style: Does it follow guidelines?
- Documentation: Is it well documented?
- Performance: Any performance concerns?
- Breaking changes: Are they necessary and documented?

### Responding to Feedback

- Be receptive to suggestions
- Ask questions if unclear
- Make requested changes
- Mark conversations as resolved when done
- Request re-review when ready

## Development Tips

### GPU Testing

```python
# Check for GPU availability
if torch.cuda.is_available():
    # GPU-specific code
    pass
else:
    # CPU fallback or skip
    pytest.skip("CUDA not available")
```

### Debugging

```bash
# Run with verbose output
pytest -v

# Run with debugging
pytest --pdb

# Run single test with prints
pytest -s tests/test_voice.py::test_specific
```

### Performance Testing

```python
import time

start = time.time()
result = function_to_test()
duration = time.time() - start
print(f"Took {duration:.2f}s")
```

## Questions?

- **General questions**: Open a discussion
- **Bug reports**: Open an issue
- **Feature requests**: Open an issue for discussion
- **Security issues**: Email maintainers privately

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Avatar Pipeline!
