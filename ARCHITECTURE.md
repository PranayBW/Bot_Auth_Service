# Project Architecture (GPM Bot - Authorization Service)

## What this service does
This codebase hosts an **Authorization Service** for a Teams/Bot solution. Its responsibilities are to:
- validate incoming requests (bot + tenant/security tokens),
- infer the user's intent from their message,
- authorize the user to proceed,
- select the correct agent for the requested intent,
- optionally enrich responses (e.g., semantic prefill),
- persist conversation/run metadata for traceability.

## Main components
- **FastAPI app**
  - Entry point that wires API routers and lifecycle hooks (startup/shutdown).
- **Authorization API**
  - Core endpoint that validates security headers/tokens, detects intent, authorizes the user, selects an agent, and returns an eligibility response.
- **Intent Classifier**
  - Maps user text -> intent (e.g., `JD_CREATE`, `JD_FETCH`, `UNKOWN_INTENT`) using keyword checks and embeddings-based similarity.
- **Agent Orchestrator**
  - Resolves which agent a user can access for a given intent and selects the primary agent.
  - Enforces an allowlist of what each agent is permitted to do (agent-to-capability/tool mapping).
- **Memory Store (PostgreSQL)**
  - Persists conversations, prompts, and runs (start/finish), enabling auditing and debugging.

## High-level request flow (Eligibility)
When a request hits the eligibility endpoint:
1. **Header validation**
   - Confirms required auth headers exist.
   - Confirms the Bot App ID matches the configured `BOT_APP_ID`.
2. **Token validation (bot authentication)**
   - **AAD token validation**
     - Fetches tenant OIDC configuration + JWKS.
     - Validates signature, issuer (tenant-scoped), and audience (`api://<GATEWAY_API_CLIENT_ID>`).
   - **Bot Framework JWT validation**
     - Fetches Bot Framework JWKS.
     - Validates signature, issuer (`https://api.botframework.com`), and audience (`BOT_APP_ID`).
3. **User identity extraction**
   - Uses `user_email` from the request payload as the user identity key (used for authorization, agent selection, and memory partitioning).
4. **Intent detection**
   - Runs intent classification on the user message text.
5. **User authorization**
   - Calls an external login/auth endpoint using the user's email.
   - If unauthorized, returns **HTTP 401** with the upstream unauthorized message.
6. **Agent selection (agent orchestrator)**
   - For authorized users, resolves and selects the primary agent for `(user_email, intent)`.
7. **Tracking + response**
   - Creates/updates conversation, prompt, and run records.
   - Returns an eligibility response (and may include semantic prefill for fetch intent).

## Agent orchestrator details
The agent orchestrator is responsible for:
- **Eligibility-to-agent resolution**: choose the correct agent based on user + intent.
- **Policy enforcement**: only allow approved capabilities/tools for a given agent (a strict allowlist).
- **Operational safety**: prevents unintended actions by disallowing tools that are not explicitly mapped to an agent.

## Security (bot authentication)
The security model validates both:
- **Tenant-scoped identity (AAD token)**
  - Ensures the caller is from the expected tenant and the token was issued for the expected audience.
- **Bot channel authenticity (Bot Framework JWT)**
  - Ensures the request is genuinely coming through the Bot Framework channel and targets your bot (`BOT_APP_ID`).

### Important configuration
Key environment settings used for security and routing:
- `TENANT_ID`: tenant boundary for issuer validation.
- `GATEWAY_API_CLIENT_ID`: expected audience for the AAD token.
- `BOT_APP_ID`: expected audience for the Bot Framework token and the bot identity check.
- `MCP_BASE_URL`: base URL for the external authorization/agent service.
- `DATABASE_URL`: Postgres connection for memory.
- `BYPASS_AUTH`: local/testing bypass (must be **disabled** in production).

### Production note
`BYPASS_AUTH` should be `False` in production deployments. When enabled, it can skip token/header validation and must only be used for controlled local development.
