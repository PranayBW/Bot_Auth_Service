import aiohttp

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:latest"


async def chat_json(
    system_prompt: str,
    user_prompt: str
):

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0
        }
    }

    async with aiohttp.ClientSession() as session:

        async with session.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload
        ) as response:

            return await response.json()