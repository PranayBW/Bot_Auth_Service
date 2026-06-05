import json
import re
import time

import httpx

from auth_service.config.settings import settings
from auth_service.ai.intent_registry import (
    UNKNOWN_INTENT,
    build_ollama_system_prompt,
    get_allowed_intents,
)


SYSTEM_PROMPT = build_ollama_system_prompt()


def _extract_json_object(content: str) -> dict:
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.IGNORECASE)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}


def _normalize_intent(value: object) -> str:
    if not isinstance(value, str):
        return UNKNOWN_INTENT

    intent = value.strip().upper()
    if intent == "UNKNOWN_INTENT":
        intent = UNKNOWN_INTENT

    return intent if intent in get_allowed_intents() else UNKNOWN_INTENT


async def detect_intent_with_ollama(text: str) -> str:
    if not settings.OLLAMA_ENABLED:
        return UNKNOWN_INTENT

    intent, success = await _detect_intent_with_ollama_model(text, settings.OLLAMA_MODEL)
    if success:
        return intent

    fallback_model = settings.OLLAMA_FALLBACK_MODEL
    if fallback_model and fallback_model != settings.OLLAMA_MODEL:
        print(f"OLLAMA INTENT FALLBACK MODEL: primary={settings.OLLAMA_MODEL} fallback={fallback_model}")
        fallback_intent, _ = await _detect_intent_with_ollama_model(text, fallback_model)
        return fallback_intent

    return UNKNOWN_INTENT


async def _detect_intent_with_ollama_model(text: str, model: str) -> tuple[str, bool]:
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "num_predict": 32,
        },
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    }

    started_at = time.perf_counter()
    print(f"OLLAMA INTENT CALL: url={base_url}/api/chat model={model}")

    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
    except httpx.TimeoutException as ex:
        elapsed = time.perf_counter() - started_at
        print(
            "OLLAMA INTENT TIMEOUT: "
            f"url={base_url}/api/chat model={model} seconds={elapsed:.2f} "
            f"timeout={settings.OLLAMA_TIMEOUT_SECONDS} error={repr(ex)}"
        )
        return UNKNOWN_INTENT, False
    except httpx.ConnectError as ex:
        elapsed = time.perf_counter() - started_at
        print(
            "OLLAMA INTENT SERVER UNREACHABLE: "
            f"url={base_url}/api/chat model={model} seconds={elapsed:.2f} "
            f"error={repr(ex)}"
        )
        return UNKNOWN_INTENT, False
    except httpx.HTTPStatusError as ex:
        elapsed = time.perf_counter() - started_at
        response_text = ex.response.text[:500] if ex.response is not None else ""
        print(
            "OLLAMA INTENT SERVER ERROR: "
            f"url={base_url}/api/chat model={model} seconds={elapsed:.2f} "
            f"status={ex.response.status_code} response={response_text!r}"
        )
        return UNKNOWN_INTENT, False
    except httpx.HTTPError as ex:
        elapsed = time.perf_counter() - started_at
        print(
            "OLLAMA INTENT REQUEST FAILED: "
            f"url={base_url}/api/chat model={model} seconds={elapsed:.2f} "
            f"error={repr(ex)}"
        )
        return UNKNOWN_INTENT, False

    elapsed = time.perf_counter() - started_at
    try:
        data = response.json()
    except ValueError as ex:
        print(
            "OLLAMA INTENT BAD JSON RESPONSE: "
            f"url={base_url}/api/chat model={model} seconds={elapsed:.2f} "
            f"response={response.text[:500]!r} error={repr(ex)}"
        )
        return UNKNOWN_INTENT, False

    content = data.get("message", {}).get("content", "")
    result = _extract_json_object(content)
    intent = _normalize_intent(result.get("intent"))

    if not result:
        print(
            "OLLAMA INTENT UNPARSEABLE CONTENT: "
            f"model={model} seconds={elapsed:.2f} content={content[:500]!r}"
        )

    print(f"OLLAMA INTENT RESPONSE: model={model} seconds={elapsed:.2f} intent={intent}")

    return intent, True
