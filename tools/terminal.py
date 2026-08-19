import logging
import subprocess
from pathlib import Path


logger = logging.getLogger(__name__)


class TerminalTool:

    def __init__(self, cwd, timeout=120):
        self.cwd = Path(cwd)
        self.cwd.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        logger.info(f"TerminalTool initialized with cwd={self.cwd}, timeout={self.timeout}s")

    def run(self, command, timeout=None):
        """Execute command with timeout and error handling."""
        
        if timeout is None:
            timeout = self.timeout

        try:
            logger.info(f"Executing command: {command[:50]}... (timeout={timeout}s)")
            
            process = subprocess.run(
                command,
                shell=True,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )

            output = process.stdout or ""

            if process.stderr:
                output += "\n[stderr]\n" + process.stderr
            
            logger.info(f"Command completed with exit code {process.returncode}")
            return process.returncode, output

        except subprocess.TimeoutExpired as e:
            error_msg = f"[timeout] command exceeded {timeout}s limit"
            logger.warning(f"Command timeout: {command[:50]}...")
            return -1, error_msg

        except FileNotFoundError as e:
            error_msg = f"[error] command not found: {str(e)}"
            logger.error(error_msg)
            return -1, error_msg

        except Exception as e:
            error_msg = str(e)
            logger.exception(f"Command execution failed: {command[:50]}...")
            return -1, error_msg