import sqlite3 as sql
from typing import List


class Database:
    def __init__(self):
        self.conn = sql.connect("database.db")
        self.cursor = self.conn.cursor()

    def create_tables(self):

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                rolenames TEXT
            )
        """
        )
        self.conn.commit()

    def get_rolenames(self, chat_id: int) -> List[str]:

        self.cursor.execute(
            """
            SELECT
                rolenames
            FROM
                chats
            where
                chat_id = (?);
        """,
            (chat_id,),
        )

        return [i[0].split(",") for i in self.cursor.fetchall()]

    def set_rolenames(self, chat_id: int, rolenames: str | list[str]):
        if isinstance(rolenames, list):
            rolenames = ",".join(rolenames)

        self.cursor.execute(
            """
            INSERT OR REPLACE INTO `chats` (`chat_id`, `rolenames`)
            VALUES (?, ?)
            """,
            (
                chat_id,
                rolenames,
            ),
        )

        self.conn.commit()

    def close(self):
        self.conn.close()
