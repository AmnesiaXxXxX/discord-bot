import sqlite3 as sql


class Database:
    def __init__(self):
        self.conn = sql.connect("database.db")
        self.cursor = self.conn.cursor()

    def create_tables(self):

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                discord_id TEXT PRIMARY KEY,
                username TEXT
            )
        """
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
