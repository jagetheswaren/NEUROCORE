# 🚀 NEUROCORE v0.4 - Deployment & Setup Guide

## ⚡ Quick Start (5 minutes)

### 1. Install Core Dependencies
```bash
cd c:\Users\jaget\NEUROCORE
pip install -r requirements.txt
```

Expected output:
```
Successfully installed rich-13.7.0 requests-2.31.0
```

### 2. Verify Ollama is Running
```bash
# On Windows, start Ollama
ollama serve

# In another terminal, test connection
curl http://127.0.0.1:11434/api/tags
```

### 3. Run NEUROCORE
```bash
python main.py
```

You should see:
```
INFO - core.model - OllamaModel initialized
INFO - core.orchestrator - NeuroCoreApp initialized
INFO - voice.speech - Speech recognition model loaded successfully
INFO - voice.tts - TextToSpeech initialized successfully
```

---

## 📦 Full Setup (10 minutes)

### Step 1: Clone/Navigate to Repository
```bash
cd c:\Users\jaget\NEUROCORE
```

### Step 2: Install All Dependencies
```bash
# Core dependencies (required)
pip install -r requirements.txt

# Voice support (recommended for full features)
pip install -r requirements-voice.txt

# Development tools (for testing)
pip install -r requirements-dev.txt
```

### Step 3: Verify Configuration
```bash
# Check settings.json exists and has required fields
cat config/settings.json
```

Expected fields:
```json
{
  "model": "qwen3:8b",
  "ollama_url": "http://127.0.0.1:11434",
  "ollama_timeout": 300,
  "command_timeout": 120,
  "logging_level": "INFO",
  "temperature": 0.7,
  "workspace": "workspace",
  "auto_approve": false,
  "sensitive": ["rm ", "sudo", "delete", "format"]
}
```

### Step 4: Ensure Ollama is Running
```bash
# Start Ollama server
ollama serve

# In another terminal, ensure model is pulled
ollama pull qwen3:8b
```

### Step 5: Start NEUROCORE
```bash
python main.py
```

### Step 6: Run Tests (Optional)
```bash
# Install test dependencies if not done in Step 2
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=core --cov=tools --cov=memory --cov=voice --cov-report=html
```

---

## 🧪 Testing Guide

### Run All Tests
```bash
cd c:\Users\jaget\NEUROCORE
pytest tests/ -v
```

### Run Tests for Specific Module
```bash
# Test model only
pytest tests/test_model.py -v

# Test orchestrator only
pytest tests/test_orchestrator.py -v

# Test terminal commands only
pytest tests/test_terminal.py -v

# Test memory database only
pytest tests/test_memory.py -v

# Test permissions only
pytest tests/test_permissions.py -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=core --cov=tools --cov=memory --cov=voice \
    --cov-report=html --cov-report=term-missing
```

Open `htmlcov/index.html` in browser to view coverage.

### Run Specific Test
```bash
# Run one test
pytest tests/test_model.py::test_health_check_success -v

# Run tests matching pattern
pytest tests/ -k "error" -v
```

---

## 📊 Monitoring & Logging

### View Live Logs
```bash
# Watch logs in real-time
tail -f logs/neurocore.log

# On Windows PowerShell
Get-Content -Path logs/neurocore.log -Wait -Tail 20
```

### Adjust Log Level
Edit `config/settings.json`:
```json
{
  "logging_level": "DEBUG"  // Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
}
```

### Log File Rotation
Current setup:
- Log file: `logs/neurocore.log`
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Console format: `%(levelname)s - %(message)s`

To implement log rotation (optional):
```python
# In main.py, modify setup_logging():
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
```

---

## 🔧 Configuration

### settings.json Fields

| Field | Type | Default | Purpose |
|---|---|---|---|
| model | string | "qwen3:8b" | Ollama model to use |
| ollama_url | string | "http://127.0.0.1:11434" | Ollama server URL |
| ollama_timeout | int | 300 | Request timeout (seconds) |
| command_timeout | int | 120 | Terminal command timeout (seconds) |
| temperature | float | 0.7 | LLM creativity (0.0-1.0) |
| workspace | string | "workspace" | Working directory for terminal |
| auto_approve | bool | false | Auto-execute safe commands |
| sensitive | array | [...] | Commands requiring approval |
| logging_level | string | "INFO" | Console log verbosity |

### Changing Timeouts
Edit `config/settings.json`:
```json
{
  "ollama_timeout": 600,    // Increase to 10 minutes
  "command_timeout": 300    // Increase to 5 minutes
}
```

### Enabling Voice Features
Ensure dependencies are installed:
```bash
pip install -r requirements-voice.txt
```

Then NEUROCORE will automatically detect and enable:
- Speech recognition (`/voice` mode)
- Text-to-speech (Tamil language)

---

## ⚠️ Troubleshooting

### Issue: "Could not connect to Ollama"
```
Error: ConnectionError: Could not connect to http://127.0.0.1:11434
```

**Solution:**
```bash
# Start Ollama service
ollama serve

# Verify it's running
curl http://127.0.0.1:11434/api/tags
```

### Issue: "Model not found"
```
Error: HTTPError 404: Model 'qwen3:8b' not found
```

**Solution:**
```bash
# Pull the model
ollama pull qwen3:8b

# Verify it's available
ollama list
```

### Issue: "No audio input device found"
```
Error: No audio input device found
```

**Solution:**
```bash
# Verify PyAudio installation
pip install --upgrade PyAudio

# Check available devices
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### Issue: "Command timeout"
```
Timeout: command exceeded 120s limit
```

**Solution:**
- Increase `command_timeout` in `config/settings.json`
- Or run commands with lower overhead
- Or optimize the command itself

### Issue: Tests are failing
```
FAILED tests/test_model.py::test_health_check_success
```

**Solution:**
```bash
# Verify all dependencies installed
pip install -r requirements-dev.txt

# Run tests with verbose output
pytest tests/ -vv --tb=long

# Check if Ollama is running (some tests may need it)
curl http://127.0.0.1:11434/api/tags
```

---

## 📈 Performance Tuning

### Memory Usage
- Ollama server: ~2GB baseline
- NEUROCORE app: ~500MB
- Total: ~2.5GB recommended

### Response Time
- First request: 2-5 seconds (model loading)
- Subsequent requests: 0.5-3 seconds (depends on model)
- Terminal commands: <1 second (typical)

### Optimizations
1. Keep Ollama running in background
2. Use a faster model if needed: `ollama pull phi:2b`
3. Reduce `temperature` for faster responses
4. Increase `ollama_timeout` if getting timeouts

---

## 🔐 Security Notes

### Permissions System
- Terminal commands require approval (unless auto_approve=true)
- Sensitive commands always require approval:
  ```json
  "sensitive": ["rm ", "sudo", "delete", "format"]
  ```

### Database Security
- Memory database stored in: `brain.db`
- No encryption by default
- To enable encryption (optional):
  ```python
  # In core/config.py, modify MemoryDatabase initialization
  from sqlcipher3 import dbapi2 as sqlite3
  ```

### API Security
- Ollama runs on localhost only (change in Ollama settings if needed)
- No authentication required (configure in Ollama if deploying remotely)

---

## 📚 Documentation Files

| File | Purpose |
|---|---|
| **COMPLETION_SUMMARY.md** | Overall project completion status |
| **IMPROVEMENTS.md** | Detailed technical improvements |
| **CHECKLIST.md** | Task-by-task completion checklist |
| **tests/README.md** | Testing guide and documentation |
| **config/settings.json** | Runtime configuration reference |

---

## 🎯 Next Steps

### Immediate Actions
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Start Ollama: `ollama serve`
- [ ] Run NEUROCORE: `python main.py`
- [ ] View logs: `tail -f logs/neurocore.log`

### Testing (Optional)
- [ ] Install dev dependencies: `pip install -r requirements-dev.txt`
- [ ] Run tests: `pytest tests/ -v`
- [ ] Generate coverage: `pytest tests/ --cov`

### Production Deployment
- [ ] Set `logging_level: "WARNING"` in settings.json
- [ ] Configure `auto_approve` safely based on your needs
- [ ] Set up log rotation for long-running instances
- [ ] Monitor `logs/neurocore.log` for errors
- [ ] Implement CI/CD pipeline for testing

### Optional Enhancements
- [ ] Add multi-language voice support
- [ ] Implement Prometheus metrics export
- [ ] Add WebSocket API for remote access
- [ ] Create Docker containerization
- [ ] Implement memory database indexing

---

## 💬 Getting Help

### Check Logs First
```bash
# View recent errors
tail -50 logs/neurocore.log | grep ERROR

# View all errors since startup
grep ERROR logs/neurocore.log
```

### Enable Debug Logging
```json
{
  "logging_level": "DEBUG"
}
```

### Run Single Test for Issue
```bash
# If model is failing
pytest tests/test_model.py -vv

# If terminal is failing
pytest tests/test_terminal.py -vv

# With full traceback
pytest tests/ -vv --tb=long
```

---

## ✨ Success Indicators

When NEUROCORE is working correctly:

✅ **Startup**
- No errors in console
- `logs/neurocore.log` contains initialization messages
- App responds to commands

✅ **Ollama Connection**
- Response times <3 seconds
- No "ConnectionError" in logs
- Model responses appear correctly

✅ **Voice (If Enabled)**
- Audio input detected when in `/voice` mode
- Transcription appears in logs
- Text-to-speech plays audio

✅ **Terminal Commands**
- Command execution succeeds
- Output appears in response
- Timeouts handled gracefully

✅ **Tests Pass**
- 62+ tests run without failures
- Coverage >80% for modified modules
- No import or syntax errors

---

**🎉 NEUROCORE v0.4 is ready for deployment!**
