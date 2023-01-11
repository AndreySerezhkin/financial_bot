import psycopg2
import traceback
from psycopg2.extras import DictCursor
from config import host, user, password, db_name


class Postgres(object):
    def __init__(self, *args, **kwargs):
        self.args = args

    def _connect(self, msg=None):
        try:
            self.conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        except Exception:
            traceback.print_exc()

    def __enter__(self, *args, **kwargs):
        self._connect()
        return (self.conn, self.cursor)

    def __exit__(self, *args):
        for c in ('cursor', 'conn'):
            try:
                obj = getattr(self, c)
                obj.close()
            except Exception:
                traceback.print_exc()
        self.args, self.dbName = None, None
