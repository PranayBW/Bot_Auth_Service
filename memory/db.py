from __future__ import annotations

import asyncpg

from auth_service.config.settings import settings

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def autoinit_schema() -> None:
    if not settings.AGENT_MEMORY_AUTOINIT:
        return

    pool = await get_pool()
    sql = (
        __import__("pathlib")
        .Path(__file__)
        .with_name("schema.sql")
        .read_text(encoding="utf-8")
    )
    async with pool.acquire() as conn:
        await conn.execute(sql)

