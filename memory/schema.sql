CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS mem_conversations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_key text NOT NULL,
  external_conversation_id text NULL,
  channel_id text NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_mem_conversations_user_external UNIQUE (user_key, external_conversation_id)
);

CREATE INDEX IF NOT EXISTS idx_mem_conversations_user_created
  ON mem_conversations (user_key, created_at DESC);

CREATE TABLE IF NOT EXISTS mem_prompts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id uuid NOT NULL REFERENCES mem_conversations(id) ON DELETE CASCADE,
  prompt_text text NOT NULL,
  prompt_hash text NOT NULL,
  edited_from_id uuid NULL REFERENCES mem_prompts(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mem_prompts_convo_created
  ON mem_prompts (conversation_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_mem_prompts_hash
  ON mem_prompts (prompt_hash);

CREATE TABLE IF NOT EXISTS mem_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id uuid NOT NULL REFERENCES mem_conversations(id) ON DELETE CASCADE,
  prompt_id uuid NOT NULL REFERENCES mem_prompts(id) ON DELETE RESTRICT,
  intent text NULL,
  agent text NULL,
  status text NOT NULL DEFAULT 'started',
  started_at timestamptz NOT NULL DEFAULT now(),
  ended_at timestamptz NULL,
  CONSTRAINT chk_mem_runs_status CHECK (status IN ('started','succeeded','failed'))
);

CREATE INDEX IF NOT EXISTS idx_mem_runs_convo_started
  ON mem_runs (conversation_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_mem_runs_intent_started
  ON mem_runs (intent, started_at DESC);

CREATE TABLE IF NOT EXISTS mem_steps (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id uuid NOT NULL REFERENCES mem_runs(id) ON DELETE CASCADE,
  step_index integer NOT NULL,
  agent text NOT NULL,
  tool text NOT NULL,
  user_query text NOT NULL,
  intent text NULL,
  success boolean NOT NULL,
  latency_ms integer NULL,
  error text NULL,
  input_payload jsonb NULL,
  output_payload jsonb NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_mem_steps_run_step UNIQUE (run_id, step_index),
  CONSTRAINT chk_mem_steps_latency CHECK (latency_ms IS NULL OR latency_ms >= 0)
);

CREATE INDEX IF NOT EXISTS idx_mem_steps_run_step
  ON mem_steps (run_id, step_index);

CREATE INDEX IF NOT EXISTS idx_mem_steps_intent_agent_tool_created
  ON mem_steps (intent, agent, tool, created_at DESC);

