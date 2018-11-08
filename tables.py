from db import Database
db_location = "example.db"

class Table(object):
    def __init__(self, query):
        self.db = Database(db_location)
        self._cur = self.db.run_query(table=query[0], contraints=query[1])

    @property
    def col_names(self):
        return [name for name, *_ in self._cur.description]

    @property
    def rows(self):
        return iter(self._cur)

