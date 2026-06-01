import re
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b" # Keep as qwen3:8b, but speed-tuned via options below

def _clean(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)   # bold
    text = re.sub(r'\*(.*?)\*',     r'\1', text)   # italic
    text = re.sub(r'#{1,6}\s*',     '',    text)   # headers
    text = re.sub(r'---+',          '',    text)   # dividers
    text = re.sub(r'`{1,3}',        '',    text)   # code ticks
    text = re.sub(r'\n{3,}',        '\n\n', text)  # excess newlines
    return text.strip()

def ask_ollama(question: str, system_prompt: str, memory: list = None) -> str:
    messages = []
    if memory:
        messages.extend(memory)
    messages.append({"role": "user", "content": question})

    payload = {
        "model": MODEL,
        "messages": messages,
        "system": system_prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 150,  # Snappy, short responses
            "num_ctx": 1024,     # Half the memory load for faster processing
            "num_thread": 8,     # Forces usage of all CPU cores
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        reply = data["message"]["content"].strip()
        reply = _clean(reply)
        return reply if reply else "...i got nothing."

    except requests.exceptions.ConnectionError:
        return "ollama isn't running. start it first!"
    except requests.exceptions.Timeout:
        return "that took too long. i gave up."
    except Exception as e:
        return f"something broke: {str(e)[:40]}"