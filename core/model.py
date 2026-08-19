import json
import logging
import requests


logger = logging.getLogger(__name__)


class OllamaModelError(Exception):
    """Custom exception for OllamaModel errors."""
    pass


class OllamaModel:

    def __init__(
        self,
        model="qwen3:8b",
        base_url="http://127.0.0.1:11434",
        temperature=0.7,
        num_predict=400,
        no_think=True,
        timeout=300
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.num_predict = num_predict
        self.no_think = no_think
        self.timeout = timeout
        self._is_available = None
        
        logger.info(
            f"Initializing OllamaModel: {model} at {base_url}"
        )

    def chat(self, message: str, system: str = None) -> str:

        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system
            })

        messages.append({
            "role": "user",
            "content": message
        })

        return self._request(messages)

    def chat_messages(self, history, system: str = None) -> str:

        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system
            })

        messages.extend(
            {
                "role": item["role"],
                "content": item["content"]
            }
            for item in history
        )

        return self._request(messages)

    def stream_chat_messages(self, history, system: str = None):
        """Stream response tokens from Ollama API."""
        
        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system
            })

        messages.extend(
            {
                "role": item["role"],
                "content": item["content"]
            }
            for item in history
        )

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "think": not self.no_think,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.num_predict
                    }
                },
                timeout=self.timeout,
                stream=True
            )

            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            content = chunk["message"]["content"]
                            if content:  # Only yield non-empty tokens
                                yield content
                    except json.JSONDecodeError:
                        continue
                        
            logger.debug("Stream completed from Ollama")
            
        except requests.exceptions.ConnectionError as e:
            error_msg = (
                f"❌ Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: ollama serve"
            )
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e
            
        except requests.exceptions.Timeout as e:
            error_msg = f"❌ Ollama request timeout ({self.timeout}s). Server may be overloaded."
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                error_msg = (
                    f"❌ Model '{self.model}' not found in Ollama. "
                    f"Pull it first: ollama pull {self.model}"
                )
            else:
                error_msg = f"❌ Ollama HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Ollama request failed: {str(e)}"
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e

    def _request(self, messages) -> str:
        """Send request to Ollama API with error handling."""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "think": not self.no_think,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.num_predict
                    }
                },
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()
            
            logger.debug(f"Received response from Ollama: {len(data.get('message', {}).get('content', ''))} chars")
            return data["message"]["content"]
            
        except requests.exceptions.ConnectionError as e:
            error_msg = (
                f"❌ Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: ollama serve"
            )
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e
            
        except requests.exceptions.Timeout as e:
            error_msg = f"❌ Ollama request timeout ({self.timeout}s). Server may be overloaded."
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                error_msg = (
                    f"❌ Model '{self.model}' not found in Ollama. "
                    f"Pull it first: ollama pull {self.model}"
                )
            else:
                error_msg = f"❌ Ollama HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Ollama request failed: {str(e)}"
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e
            
        except (KeyError, ValueError) as e:
            error_msg = f"❌ Invalid response from Ollama: {str(e)}"
            logger.error(error_msg)
            raise OllamaModelError(error_msg) from e
    
    def health_check(self) -> bool:
        """Check if Ollama server is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            self._is_available = True
            logger.info("✓ Ollama server is available")
            return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            self._is_available = False
            return False