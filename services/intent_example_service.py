from auth_service.utils.sql_loader import load_sql
from auth_service.config.database import db


class IntentDatasetService:

    async def get_examples(
        self,
        intent_code: str
    ) -> list[str]:

        query = load_sql(
            "get_intent_example_list.sql"
        )

        rows = await self.db.fetch(
            query,
            intent_code
        )

        return [
            row["example_text"]
            for row in rows
        ]