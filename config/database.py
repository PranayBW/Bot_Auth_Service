import asyncpg

from auth_service.config.settings import settings


class Database:

    async def fetch(
        self,
        query: str,
        *args
    ):

        conn = await asyncpg.connect(
            settings.DATABASE_URL
        )

        try:

            return await conn.fetch(
                query,
                *args
            )

        finally:

            await conn.close()

    async def fetchrow(
        self,
        query: str,
        *args
    ):

        conn = await asyncpg.connect(
            settings.DATABASE_URL
        )

        try:

            return await conn.fetchrow(
                query,
                *args
            )

        finally:

            await conn.close()

    async def execute(
        self,
        query: str,
        *args
    ):

        conn = await asyncpg.connect(
            settings.DATABASE_URL
        )

        try:

            return await conn.execute(
                query,
                *args
            )

        finally:

            await conn.close()


db = Database()