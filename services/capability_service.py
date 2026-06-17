from auth_service.config.database import db

from auth_service.utils.sql_loader import load_sql


class CapabilityService:

    async def get_org_capabilities(
        self,
        org_id: int
    ):

        query = load_sql(
            "sql/get_org_services.sql"
        )

        rows = await db.fetch(
            query,
            org_id
        )

        return [
            dict(row)
            for row in rows
        ]