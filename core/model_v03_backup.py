import requests


class OllamaModel:

    def __init__(
        self,
        model="qwen3:8b",
        base_url="http://127.0.0.1:11434"
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def chat(self, message: str) -> str:

        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": message + "\n/no_think"
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300
                }
            },
            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]