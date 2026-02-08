# Avatar Pipeline Test Suite

Comprehensive test suite for the Avatar Pipeline project.

## Overview

This test suite provides extensive coverage for all modules:
- Configuration and hardware detection
- VRAM management
- Voice cloning and synthesis
- Avatar generation and face detection
- Video lip-sync and encoding
- Orchestration and job management
- API models and endpoints
- CLI commands

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

### Run specific test files
```bash
# Config tests
pytest tests/test_config/

# Voice tests
pytest tests/test_voice/

# API tests
pytest tests/test_api/
```

### Run by markers
```bash
# Skip slow tests (model loading)
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Skip GPU tests
pytest -m "not gpu"
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_config/
│   ├── test_hardware.py     # GPU detection tests
│   └── test_settings.py     # Config loading tests
├── test_utils/
│   └── test_vram.py         # VRAM manager tests
├── test_voice/
│   └── test_profiles.py     # Profile manager tests
├── test_orchestration/
│   └── test_jobs.py         # Job dataclass tests
├── test_api/
│   └── test_models.py       # Pydantic model tests
└── test_cli.py              # CLI command tests
```

## Test Categories

### Unit Tests
- Fast, isolated tests
- Mock external dependencies
- Test individual functions/classes
- Run by default

### Integration Tests
- Test component interactions
- May involve file I/O
- Marked with `@pytest.mark.integration`

### Slow Tests
- Require model loading
- Take significant time
- Marked with `@pytest.mark.slow`
- Skip by default

### GPU Tests
- Require CUDA/GPU hardware
- Marked with `@pytest.mark.gpu`
- Skip by default

## Key Fixtures

### Configuration
- `sample_config`: Sample configuration dict
- `sample_config_file`: Temporary YAML config file
- `temp_storage`: Temporary storage directory

### Mocking
- `mock_torch_cuda`: Mock CUDA without GPU
- `mock_torch_cuda_available`: Mock CUDA with GPU
- `mock_vram_manager`: Mock VRAM manager
- `mock_ffmpeg`: Mock FFmpeg subprocess calls

### Test Data
- `sample_audio_file`: Minimal WAV file
- `sample_image_file`: Minimal PNG image
- `sample_video_file`: Minimal video file path
- `mock_voice_profile`: Mock voice profile
- `mock_avatar_profile`: Mock avatar profile

## Writing New Tests

### Test Naming
```python
# Good
def test_load_config_with_valid_file():
    """Test loading config from valid YAML file."""

# Bad
def test_config():
    pass
```

### Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange - Set up test data
    config = {"key": "value"}

    # Act - Execute the code
    result = process_config(config)

    # Assert - Verify the result
    assert result["key"] == "value"
```

### Using Mocks
```python
def test_with_mock(mocker):
    # Mock external dependency
    mock_model = mocker.MagicMock()
    mock_model.predict.return_value = "output"
    mocker.patch("src.module.Model", return_value=mock_model)

    # Test code that uses the model
    result = function_that_uses_model()

    # Verify mock was called correctly
    mock_model.predict.assert_called_once()
```

## Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| config/ | 90%+ |
| utils/ | 90%+ |
| orchestration/jobs.py | 100% |
| api/models.py | 90%+ |
| Other modules | 70%+ |

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Nightly builds

CI configuration skips slow and GPU tests by default.

## Troubleshooting

### Tests fail with "No module named 'torch'"
Mock torch imports are configured in conftest.py. Ensure you're not importing torch directly in test files.

### Tests fail with CUDA errors
Use `mock_torch_cuda` or `mock_torch_cuda_available` fixtures to avoid real GPU operations.

### Integration tests are flaky
Integration tests involving file I/O should use `tmp_path` fixture for isolation.

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure tests cover happy path, edge cases, and errors
3. Update this README if adding new test categories
4. Maintain coverage above targets
