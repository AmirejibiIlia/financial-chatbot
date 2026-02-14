import requests


class OllamaLLM:
    """Wrapper around Ollama's chat API."""

    def __init__(self, model: str, url: str):
        self.model = model
        self.url = url

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        resp = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()
