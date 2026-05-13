INTENT_MAP = {
    "start jd creation": "JD_CREATE",
    "start jd process": "JD_CREATE",
    "create jd": "JD_CREATE",
    "fetch jd": "JD_FETCH"
}


def detect_intent(text: str):

    normalized = text.lower().strip()

    return INTENT_MAP.get(normalized)