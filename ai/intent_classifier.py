from sklearn.metrics.pairwise import (
    cosine_similarity
)

from auth_service.ai.embedding_model import get_model

# ----------------------------------------------------
# JD CREATE EXAMPLES
# ----------------------------------------------------

JD_CREATE_EXAMPLES = [

    "create jd",
    "create a jd",
    "generate jd",
    "new jd",
    "create job description",
    "generate job description",

    "we need a react developer",
    "hire a python developer",
    "need a backend engineer",
    "open a new position",
    "start hiring for java developer",

    "create a jd for react dev",
    "prepare jd for software engineer",
    "draft a jd for python developer",

    "create a jd for react dev in it department",
    "create a jd for software developer role",
    "generate jd for backend developer",

    "i want to hire a react developer",
    "we are looking for a backend engineer",

    "raise a hiring request",
    "create manpower requirement",
    "open a requisition",

    "need jd",
    "jd creation",
    # "start jd process",
    # "start jd creation",

    "crt jd",
    "create jdd",
    "genrate jd"
]

# ----------------------------------------------------
# JD FETCH EXAMPLES
# ----------------------------------------------------

JD_FETCH_EXAMPLES = [

    "fetch jd",
    "get jd",
    "show jd",
    "retrieve jd",
    "find jd",
    "search jd",

    "show me the jd",
    "get the job description",
    "retrieve job description",

    "show open jd",
    "find hiring requirement",
    "retrieve hiring document",

    "fetch jd for react developer",
    "show jd for backend engineer",
    "find jd for python developer",

    "can you show the jd",
    "i want to see the job description",

    "get all jd",
    "list all jd",
    "show all job descriptions",

    "show jd from it department",
    "find jd for senior developer",

    "jd fetch",
    "fetch job desc",

    "ftech jd",
    "fetsh jd",

    # Edit JD should map to fetch (retrieve existing JD first)
    "edit jd",
    "edit the jd",
    "edit job description",
    "update jd",
    "update the jd",
    "modify jd",
    "modify job description",
    "revise jd",
    "change jd",
    "change job description",

    # Edit/update existing JD with role/department qualifiers
    "edit jd for react developer",
    "edit the jd for react developer",
    "update jd for react developer",
    "modify jd for react developer",

    "edit jd for backend engineer",
    "update jd for software engineer",
    "revise jd for python developer",
    "change job description for java developer",

    "edit jd for senior developer",
    "update jd for lead engineer",
    "modify job description for frontend developer",

    "edit jd from it department",
    "update jd for react developer in it department",
    "modify job description for backend engineer in engineering department",
    "revise jd for software developer role",
    "change jd for backend developer"
]

# ----------------------------------------------------
# AMBIGUOUS / MENU EXAMPLES
# ----------------------------------------------------

UNKOWN_INTENT_EXAMPLES = [
    # Generic start/begin prompts (no create vs fetch)
    "start jd",
    "start jd process",
    "start job description",
    "start job description process",
    "start jd workflow",
    "start jd flow",
    "begin jd process",
    "open jd process",
    "launch jd process",
    "init jd process",
    "initialize jd process",

    # Menu/help style prompts
    "jd menu",
    "show jd menu",
    "open jd menu",
    "jd options",
    "jd actions",
    "help jd",
    "jd help",
    "what can i do with jd",
    "what can i do in jd",
    "how to use jd",

    # Ambiguous "work on jd" prompts
    "jd process",
    "jd workflow",
    "job description workflow",
    "job description process",
    "jd flow",
    "i want to do jd",
    "i need jd",
    "i need job description",
    "jd",
    "job description",

    # Ambiguous fetch/create process wording
    "start fetch jd process",
    "start fetching jd process",
    "start fetching jd",
    "start jd fetch process",
    "start create jd process",
    "start creating jd process",
    "start creating jd",
]

# ----------------------------------------------------
# INTENT DATASET
# ----------------------------------------------------

INTENT_DATASET = {
    "JD_CREATE": JD_CREATE_EXAMPLES,
    "JD_FETCH": JD_FETCH_EXAMPLES,
    "UNKOWN_INTENT": UNKOWN_INTENT_EXAMPLES,
}

# ----------------------------------------------------
# PRECOMPUTE EMBEDDINGS
# ----------------------------------------------------

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

# ----------------------------------------------------
# DETECT INTENT
# ----------------------------------------------------


def detect_intent(text: str):
    model = get_model()
    intent_embeddings = _ensure_initialized()

    query_embedding = model.encode([text])[0]

    best_intent = None

    best_score = -1

    for intent, embeddings in intent_embeddings.items():

        similarities = cosine_similarity(
            [query_embedding],
            embeddings
        )[0]

        score = max(similarities)

        print(f"{intent} SCORE:", score)

        if score > best_score:

            best_score = score

            best_intent = intent

    print("BEST INTENT:", best_intent)
    print("BEST SCORE:", best_score)

    # ------------------------------------------------
    # CONFIDENCE THRESHOLD
    # ------------------------------------------------

    if best_score < 0.55:

        return "UNKOWN_INTENT"

    return best_intent
