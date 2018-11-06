from db import Database
db_location = "spot.db"

class Table(object):
    def __init__(self, table):
        self.db = Database(db_location)
        if table == "example":
            print ("making table")
            self.db.create_hardcoded_table()
            self.cur = self.db.get_example()

    @property
    def col_names(self):
        return self.cur.description

    @property
    def rows(self):
        return iter(self.cur)

