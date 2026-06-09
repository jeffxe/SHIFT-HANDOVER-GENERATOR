import requests

# Create a persistent session to keep TCP connections alive across multiple sequential requests
_session = requests.Session()

def call_ollama(prompt: str, format: str = None, num_predict: int = 2048) -> str:
    try:
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 4096,       # Set context window to 4096 to prevent input context truncation
                "temperature": 0.2,    # Keep temperature low for deterministic support formatting
                "num_predict": num_predict  # Limit generation length to avoid runaway generation
            }
        }
        if format:
            payload["format"] = format

        response = _session.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=120
        )

        return response.json()["response"]

    except Exception as e:
        return f"[Ollama Error] {str(e)}"