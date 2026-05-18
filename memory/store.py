from __future__ import annotations

import hashlib
import uuid
from typing import Any

from auth_service.memory.db import get_pool


def hash_prompt(text: str) -> str:
    normalized = " ".join((text or "").strip().split()).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


async def get_or_create_conversation(
    *,
    user_key: str,
    external_conversation_id: str | None,
    channel_id: str | None,
) -> uuid.UUID:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO mem_conversations (user_key, external_conversation_id, channel_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_key, external_conversation_id)
            DO UPDATE SET channel_id = COALESCE(EXCLUDED.channel_id, mem_conversations.channel_id)
            RETURNING id
            """,
            user_key,
            external_conversation_id,
            channel_id,
        )
    return uuid.UUID(str(row["id"]))


async def create_prompt(
    *,
    conversation_id: uuid.UUID,
    prompt_text: str,
    edited_from_id: uuid.UUID | None = None,
) -> uuid.UUID:
    pool = await get_pool()
    prompt_hash = hash_prompt(prompt_text)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO mem_prompts (conversation_id, prompt_text, prompt_hash, edited_from_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            conversation_id,
            prompt_text,
            prompt_hash,
            edited_from_id,
        )
    return uuid.UUID(str(row["id"]))


async def create_run(
    *,
    conversation_id: uuid.UUID,
    prompt_id: uuid.UUID,
    intent: str | None,
    agent: str | None,
) -> uuid.UUID:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO mem_runs (conversation_id, prompt_id, intent, agent, status)
            VALUES ($1, $2, $3, $4, 'started')
            RETURNING id
            """,
            conversation_id,
            prompt_id,
            intent,
            agent,
        )
    return uuid.UUID(str(row["id"]))


async def get_run_agent(*, run_id: uuid.UUID) -> str | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT agent FROM mem_runs WHERE id = $1", run_id)
    if not row:
        return None
    value = row["agent"]
    return str(value) if value is not None else None


async def finish_run(*, run_id: uuid.UUID, status: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE mem_runs
            SET status = $2,
                ended_at = now()
            WHERE id = $1
            """,
            run_id,
            status,
        )


async def next_step_index(*, run_id: uuid.UUID) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT COALESCE(MAX(step_index), -1) AS m FROM mem_steps WHERE run_id = $1",
            run_id,
        )
    return int(row["m"]) + 1


async def log_step(
    *,
    run_id: uuid.UUID,
    agent: str,
    tool: str,
    user_query: str,
    intent: str | None,
    success: bool,
    latency_ms: int | None,
    error: str | None,
    input_payload: Any | None = None,
    output_payload: Any | None = None,
) -> None:
    pool = await get_pool()
    step_index = await next_step_index(run_id=run_id)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO mem_steps (
              run_id, step_index, agent, tool, user_query, intent,
              success, latency_ms, error, input_payload, output_payload
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
            """,
            run_id,
            step_index,
            agent,
            tool,
            user_query,
            intent,
            success,
            latency_ms,
            error,
            input_payload,
            output_payload,
        )
