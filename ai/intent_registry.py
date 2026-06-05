from dataclasses import dataclass


UNKNOWN_INTENT = "UNKOWN_INTENT"


@dataclass(frozen=True)
class IntentDefinition:
    intent: str
    form: str
    description: str
    examples: tuple[str, ...]
    clear_patterns: tuple[str, ...] = ()
    domain_signals: tuple[str, ...] = ()


INTENT_DEFINITIONS = {
    "JD_CREATE": IntentDefinition(
        intent="JD_CREATE",
        form="JD_CREAT_FORM",
        description=(
            "User wants to create, draft, generate, hire for, open, or raise a "
            "new job description, role, position, requisition, or manpower requirement."
        ),
        examples=(
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
            "generate jd for backend developer",
            "i want to hire a react developer",
            "raise a hiring request",
            "create manpower requirement",
            "open a requisition",
            "new role in it java and python",
        ),
        clear_patterns=(
            r"\bcreate\s+(a\s+)?(jd|job description)\b",
            r"\bgenerate\s+(a\s+)?(jd|job description)\b",
            r"\bprepare\s+(a\s+)?(jd|job description)\b",
            r"\bdraft\s+(a\s+)?(jd|job description)\b",
        ),
        domain_signals=(
            "jd",
            "job description",
            "role",
            "position",
            "opening",
            "requisition",
            "manpower",
            "hire",
            "hiring",
            "developer",
            "engineer",
            "recruit",
            "recruiting",
            "recruitment",
            "programmer",
            "coder",
            "staff",
        ),
    ),
    "JD_FETCH": IntentDefinition(
        intent="JD_FETCH",
        form="JD_FETCH_FORM",
        description=(
            "User wants to search, show, view, fetch, retrieve, list, edit, "
            "update, modify, change, or review an existing job description."
        ),
        examples=(
            "fetch jd",
            "get jd",
            "show jd",
            "retrieve jd",
            "find jd",
            "search jd",
            "show me the jd",
            "get the job description",
            "show open jd",
            "find hiring requirement",
            "fetch jd for react developer",
            "show jd for backend engineer",
            "get all jd",
            "list all jd",
            "show jd from it department",
            "edit jd",
            "update jd",
            "modify jd",
            "revise jd",
            "change job description",
            "bring the old backend developer requirement",
            "review the existing backend engineer job description",
        ),
        clear_patterns=(
            r"\bfetch\s+(a\s+)?(jd|job description)\b",
            r"\bget\s+(a\s+)?(jd|job description)\b",
            r"\bshow\s+(me\s+)?(a\s+)?(jd|job description)\b",
            r"\bfind\s+(a\s+)?(jd|job description)\b",
            r"\blist\s+(all\s+)?(jd|job descriptions)\b",
            r"\b(edit|update|modify|revise|change)\s+(a\s+)?(jd|job description)\b",
        ),
        domain_signals=(
            "jd",
            "job description",
            "existing",
            "old",
            "current",
            "previous",
            "requirement",
            "developer",
            "engineer",
            "programmer",
            "coder",
        ),
    ),
    "SCHEDULE_MEETING": IntentDefinition(
        intent="SCHEDULE_MEETING",
        form="SCHEDULE_MEETING_FORM",
        description=(
            "User wants to schedule, arrange, book, set up, or reschedule an "
            "interview or meeting for a candidate with an interviewer."
        ),
        examples=(
            "schedule meeting",
            "arrange meeting",
            "book meeting",
            "reschedule meeting",
            "schedule interview",
            "schedule an interview",
            "arrange interview for candidate",
            "book interview with interviewer",
            "set up interview for rahul tomorrow",
            "schedule java candidate interview with manager",
            "reschedule candidate interview",
            "plan interview round for python developer candidate",
            "fix interview slot for candidate and interviewer",
        ),
        clear_patterns=(
            r"\b(schedule|arrange|book|setup|set up|reschedule|plan|fix)\s+(an\s+)?(interview|meeting)\b",
        ),
        domain_signals=(
            "interview",
            "interviewer",
            "candidate",
            "round",
            "slot",
            "schedule",
            "reschedule",
            "meeting",
        ),
    ),
    "GET_CANDIDATE_LIST": IntentDefinition(
        intent="GET_CANDIDATE_LIST",
        form="GET_CANDIDATE_LIST_FORM",
        description=(
            "User wants to get, view, fetch, show, search, or list candidates, "
            "applicants, profiles, resumes, or shortlisted candidates."
        ),
        examples=(
            "get candidate list",
            "show candidate list",
            "fetch candidates",
            "list all candidates",
            "show shortlisted candidates",
            "get applicants for java role",
            "show profiles for python developer opening",
            "fetch resume list for backend engineer",
            "candidate pipeline for it department",
        ),
        clear_patterns=(
            r"\b(get|show|fetch|list|find|search)\s+(the\s+)?(candidate|candidates|candidate list|applicants|profiles|resumes)\b",
        ),
        domain_signals=(
            "candidate",
            "candidates",
            "applicant",
            "applicants",
            "profile",
            "profiles",
            "resume",
            "resumes",
            "shortlisted",
            "pipeline",
        ),
    ),
    "GET_PERSON_SCHEDULE": IntentDefinition(
        intent="GET_PERSON_SCHEDULE",
        form="GET_PERSON_SCHEDULE_FORM",
        description=(
            "User wants to get, view, fetch, check, or show an interview schedule "
            "for a candidate, interviewer, panel member, or person."
        ),
        examples=(
            "get interview schedule",
            "show interview schedule",
            "fetch candidate interview schedule",
            "show interviewer schedule",
            "check rahul interview schedule",
            "get schedule for interviewer priya",
            "show candidate schedule for tomorrow",
            "fetch interview calendar for a person",
            "what interviews are scheduled for this candidate",
        ),
        clear_patterns=(
            r"\b(get|show|fetch|check|view)\s+(the\s+)?(interview\s+)?schedule\b",
            r"\b(get|show|fetch|check|view)\s+schedule\s+(for|from)\s+(candidate|interviewer|person|panel)\b",
        ),
        domain_signals=(
            "interview schedule",
            "schedule",
            "calendar",
            "candidate",
            "interviewer",
            "panel",
            "person",
        ),
    ),
}


UNKNOWN_EXAMPLES = (
    "start jd",
    "start jd process",
    "jd menu",
    "show jd menu",
    "jd options",
    "help jd",
    "what can i do with jd",
    "jd",
    "job description",
    "i want to do jd",
    "create a leave request",
    "show my payslip",
    "update employee address",
    "fetch attendance report",
    "apply for reimbursement",
    "need java and python training for it team",
    "hire status report is needed",
    "new policy for developer onboarding",
)


def get_intent_dataset() -> dict[str, tuple[str, ...]]:
    dataset = {
        intent: definition.examples
        for intent, definition in INTENT_DEFINITIONS.items()
    }
    dataset[UNKNOWN_INTENT] = UNKNOWN_EXAMPLES
    return dataset


def get_allowed_intents() -> set[str]:
    return {*INTENT_DEFINITIONS.keys(), UNKNOWN_INTENT}


def get_form_for_intent(intent: str | None) -> str | None:
    if not intent:
        return None
    if intent == UNKNOWN_INTENT:
        return "JD_MENU"
    definition = INTENT_DEFINITIONS.get(intent)
    return definition.form if definition else None


def get_clear_patterns() -> tuple[str, ...]:
    patterns: list[str] = []
    for definition in INTENT_DEFINITIONS.values():
        patterns.extend(definition.clear_patterns)
    return tuple(patterns)


def iter_clear_patterns() -> tuple[tuple[str, str], ...]:
    patterns: list[tuple[str, str]] = []
    for definition in INTENT_DEFINITIONS.values():
        for pattern in definition.clear_patterns:
            patterns.append((definition.intent, pattern))
    return tuple(patterns)


def has_domain_signal(text: str, intent: str | None = None) -> bool:
    text_lower = text.lower()
    definitions = (
        [INTENT_DEFINITIONS[intent]]
        if intent in INTENT_DEFINITIONS
        else INTENT_DEFINITIONS.values()
    )

    return any(
        signal in text_lower
        for definition in definitions
        for signal in definition.domain_signals
    )


def build_ollama_system_prompt() -> str:
    allowed = "\n".join([*INTENT_DEFINITIONS.keys(), UNKNOWN_INTENT])
    rules = "\n".join(
        f"{definition.intent}: {definition.description}"
        for definition in INTENT_DEFINITIONS.values()
    )

    return f"""
You classify HR workflow requests.

Return only JSON with this shape:
{{"intent":"JD_CREATE"}}

Allowed intent values:
{allowed}

Rules:
{rules}
{UNKNOWN_INTENT}: Use this when the request is unclear, asks only for help/menu/options, is unrelated to the allowed intents, or asks to discuss/talk about/explain requirements rather than performing an action.

Important:
- Only return one of the allowed intent values.
- Do not classify leave, payslip, attendance, reimbursement, employee address, training, reports, or policy requests as these intents.
- If the text is related to hiring but does not clearly match one allowed intent (e.g. asking to discuss, talk about, chat, or explain a requirement or job description rather than creating, fetching, or scheduling), return {UNKNOWN_INTENT}.
- Do not explain.
- Do not add extra fields.
""".strip()
