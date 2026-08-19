# NEUROCORE Unit Tests

Comprehensive unit test suite for the NEUROCORE AI assistant, covering all core modules and error handling.

## Installation

First, install test dependencies:

```bash
pip install -r requirements-dev.txt
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ --cov=core --cov=tools --cov=memory --cov=voice --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_model.py
pytest tests/test_orchestrator.py
pytest tests/test_terminal.py
pytest tests/test_memory.py
pytest tests/test_permissions.py
```

### Run specific test class or method
```bash
pytest tests/test_model.py::TestOllamaModel::test_request_success
pytest tests/test_orchestrator.py::TestOrchestrator::test_run_friend_mode
```

## Test Coverage

The test suite covers:

### core/model.py (OllamaModel)
- ✅ Initialization with settings
- ✅ Successful API requests
- ✅ Connection error handling
- ✅ Timeout handling
- ✅ HTTP error handling (404, 500)
- ✅ Malformed response handling
- ✅ Health check functionality
- ✅ Chat with conversation history

### core/orchestrator.py (Orchestrator)
- ✅ Initialization of all subsystems
- ✅ Running in different modes (friend, plan, terminal, build, voice)
- ✅ Error handling for Ollama failures
- ✅ General exception handling
- ✅ Memory save/retrieve operations
- ✅ Conversation history management
- ✅ Mode switching

### tools/terminal.py (TerminalTool)
- ✅ Initialization with working directory
- ✅ Successful command execution
- ✅ stderr output capture
- ✅ Timeout handling
- ✅ Command not found errors
- ✅ Generic exception handling
- ✅ Configured timeout usage
- ✅ UTF-8 encoding handling

### memory/database.py (MemoryDatabase)
- ✅ Database initialization
- ✅ Table creation
- ✅ Save single and multiple memories
- ✅ Retrieve all memories
- ✅ Memory ordering (most recent first)
- ✅ Custom category handling
- ✅ Error handling for operations
- ✅ Unicode content preservation

### core/permissions.py (PermissionManager)
- ✅ Initialization with settings
- ✅ Auto-approve command detection
- ✅ Sensitive command detection
- ✅ Permission checking by mode
- ✅ Git command handling
- ✅ Case-insensitive matching
- ✅ Partial command matching

## Test Structure

Each test file follows this structure:

```python
class TestClassName:
    """Test ClassName."""
    
    def test_feature_description(self, fixtures):
        """Test specific feature."""
        # Arrange
        # Act
        # Assert
```

## Fixtures (conftest.py)

Available pytest fixtures:

- `temp_db`: Temporary SQLite database for testing
- `settings`: Default test settings
- `mock_ollama_response`: Mock Ollama API response
- `mock_requests`: Mock requests library for API calls
- `mock_subprocess`: Mock subprocess for terminal commands
- `mock_memory_db`: Mock memory database instance
- `mock_speech_recognizer`: Mock speech recognizer
- `mock_tts`: Mock text-to-speech

## Error Cases

All test files include comprehensive error case coverage:

- Network failures (ConnectionError, Timeout)
- File system errors (FileNotFoundError)
- Invalid data (malformed JSON, KeyError)
- Database errors (sqlite3.Error)
- Subprocess errors (TimeoutExpired, CalledProcessError)

## Continuous Integration

For CI/CD pipelines, run:

```bash
pytest tests/ --cov=core --cov=tools --cov=memory --cov=voice \
    --cov-report=xml --junitxml=test-results.xml -v
```

## Known Limitations

- Voice module tests use mocks (faster-whisper, piper-tts) - not end-to-end testing
- Ollama server must be running for integration tests
- Some platform-specific tests (Windows audio) may skip on other systems

## Contributing

When adding new tests:

1. Follow existing test structure and naming conventions
2. Use descriptive test names: `test_feature_expected_behavior`
3. Include docstrings explaining what is being tested
4. Mock external dependencies (Ollama, filesystem, subprocess)
5. Test both success and error cases
6. Use fixtures from conftest.py where applicable

## Debugging Tests

Run with extra output:

```bash
pytest tests/ -vv -s
```

Use breakpoints with debugger:

```bash
pytest tests/ --pdb  # Drop to debugger on failure
```

## Performance

Expected test suite runtime: **< 5 seconds** (all tests)

Individual test runtime: **< 500ms** per test
