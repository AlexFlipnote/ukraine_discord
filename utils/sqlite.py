import sqlite3


def dict_factory(cursor, row):
    d = {}
    for index, col in enumerate(cursor.description):
        d[col[0]] = row[index]
    return d


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(
            "storage.db", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.conn.row_factory = dict_factory
        self.db = self.conn.cursor()

    def execute(self, sql: str, prepared: tuple = (), commit: bool = True):
        """ Execute SQL command with args for 'Prepared Statements' """
        try:
            data = self.db.execute(sql, prepared)
        except Exception as e:
            return f"{type(e).__name__}: {e}"

        status_word = sql.split(' ')[0].upper()
        status_code = data.rowcount if data.rowcount > 0 else 0
        if status_word == "SELECT":
            status_code = len(data.fetchall())

        return f"{status_word} {status_code}"

    def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS articles (
            post_id TEXT NOT NULL,
            text TEXT NOT NULL,
            video TEXT,
            image TEXT,
            source TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (post_id)
        );
        """

        return self.execute(query)

    def fetch(self, sql: str, prepared: tuple = ()):
        """ Fetch DB data with args for 'Prepared Statements' """
        data = self.db.execute(sql, prepared).fetchall()
        return data

    def fetchrow(self, sql: str, prepared: tuple = ()):
        """ Fetch DB row (one row only) with args for 'Prepared Statements' """
        data = self.db.execute(sql, prepared).fetchone()
        return data
