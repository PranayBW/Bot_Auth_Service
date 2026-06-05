import re

from sklearn.metrics.pairwise import cosine_similarity

from auth_service.ai.embedding_model import get_model
from auth_service.ai.intent_registry import (
    UNKNOWN_INTENT,
    get_intent_dataset,
    has_domain_signal,
    iter_clear_patterns,
)


INTENT_DATASET = get_intent_dataset()

_intent_embeddings: dict[str, object] | None = None


def _ensure_initialized() -> dict[str, object]:
    global _intent_embeddings
    if _intent_embeddings is not None:
        return _intent_embeddings

    model = get_model()
    embeddings_map: dict[str, object] = {}
    for intent, examples in INTENT_DATASET.items():
        embeddings_map[intent] = model.encode(examples)

    _intent_embeddings = embeddings_map
    return embeddings_map


def _detect_clear_intent(text_lower: str) -> str | None:
    for intent, pattern in iter_clear_patterns():
        if re.search(pattern, text_lower):
            return intent

    return None


def detect_intent(text: str):
    text_lower = text.lower().strip()

    clear_intent = _detect_clear_intent(text_lower)
    if clear_intent:
        return clear_intent

    model = get_model()
    intent_embeddings = _ensure_initialized()
    query_embedding = model.encode([text])[0]

    best_intent = None
    best_score = -1

    for intent, embeddings in intent_embeddings.items():
        similarities = cosine_similarity([query_embedding], embeddings)[0]
        score = max(similarities)

        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score < 0.58:
        return UNKNOWN_INTENT

    if best_intent != UNKNOWN_INTENT and best_score < 0.72:
        if not has_domain_signal(text, best_intent):
            return UNKNOWN_INTENT

    return best_intent
