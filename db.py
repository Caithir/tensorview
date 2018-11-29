import contextlib
import sqlite3
from collections import namedtuple


class Query(namedtuple('Query', ('param', 'comparator', 'value'))):
    def __repr__(self):
        return str(self.param)+str(self.comparator)+str(self.value)

    def __str__(self):
        return str(self.param)+str(self.comparator)+str(self.value)

class Database(object):

    def __init__(self):
        # You need to call the build database function before you can make instances of it
        self._conn = Connection(sqlite3.connect(self.db_name))

    @classmethod
    def build_database(cls, db_filename, experiments, rebuild=True):
        setattr(Database, "db_name", db_filename)
        if rebuild:
            db = cls()
            db._create_experiment_table()
            db._create_run_table()
            db._create_hyperparameter_table()
            db._parse_logdir_output(experiments)

    def run_query(self, table, query=None, order_by=None):
        if not query:
            query = (Query('1', '=', '1'),)
        if not order_by:
            order_by = 'rid'
        sql_query = f'''SELECT * FROM {table}
                    WHERE {" and ".join([str(query)
                    for query in query])}
                    order by {order_by}'''
        return self._conn.execute(sql_query)

    def metric_aggregate(self, eid,  num_values, query=None, order_by=None):
        if not query:
            query = (Query('1', '=', '1'),)
        if not order_by:
            order_by = 'rid'
        sql_query = f'''SELECT rid, avg_val
                        FROM (SELECT rid, AVG(val) avg_val
                              FROM Metric_{query.param}
                              WHERE eid = {eid}
                              GROUP BY rid)
                        WHERE avg_val {query.comparator} {query.value}
                        ORDER BY {order_by}'''
        return self._conn.execute(sql_query)

    def _cursor(self):
        return contextlib.closing(self._conn.cursor())

    def _parse_logdir_output(self, logdir_kwargs):
        self.update_tables_from_logdir(logdir_kwargs)
        self.populate_tables_from_logdir(logdir_kwargs)

    def update_tables_from_logdir(self, experiments):
        self.eids = {}
        for eid, (experiment_name, runs) in enumerate(experiments.items()):
            with self._cursor() as c:
                self.eids[experiment_name] = eid
                c.execute(f"INSERT OR IGNORE INTO Experiment VALUES({eid}, '{experiment_name}');")
                for rid, (run_name, params) in enumerate(runs.items()):
                    params['id'] = rid
                    c.execute(f"INSERT OR IGNORE INTO Run VALUES({eid}, {rid}, '{run_name}');")
                    c.execute(f"INSERT OR IGNORE INTO HyperParameter (eid, rid) VALUES({eid}, {rid})")

    def populate_tables_from_logdir(self, experiments):
        for experiment_name, runs in experiments.items():
            eid = self.eids[experiment_name]
            for run, params in runs.items():
                rid = params['id']
                with self._conn as c:
                    # Hyper parameters
                    for hyper in params['hyper']:
                        col = [i[1] for i in c.execute("PRAGMA table_info(HyperParameter);")]
                        # Type check
                        is_str = isinstance(params['hyper'][hyper], str)
                        str_format = "'" if is_str else ""
                        if hyper not in col:
                            c.execute(f"ALTER TABLE HyperParameter ADD {hyper} {'varchar(255)' if is_str else 'real'};")
                            col += [hyper]

                        c.execute(f"""UPDATE HyperParameter SET {hyper} = {str_format}{params['hyper'][hyper]}{str_format}
                                      WHERE (eid = {eid} AND rid = {rid});""")

                    # Metric parameters
                    # Metric tables are stored in "Metric_data_stuff" format
                    for metric in params['metric']:
                        name = "Metric_" + metric.replace('/', '_')
                        c.execute(f'''CREATE TABLE IF NOT EXISTS {name} (
                                     eid INTEGER NOT NULL REFERENCES Experiment (eid),
                                     rid INTEGER NOT NULL REFERENCES Run (rid),
                                     ind INTEGER NOT NULL,
                                     val REAL NOT NULL,
                                     PRIMARY KEY (eid, rid, ind));''')

                        for (i, v) in enumerate(params['metric'][metric]):
                            c.execute(f"INSERT OR IGNORE INTO {name} VALUES({eid}, {rid}, {i}, {v});")

    def _create_experiment_table(self):
        with self._cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS Experiment (
                         eid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                         name varchar(255) NOT NULL);''')

    def _create_run_table(self):
        with self._cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS Run (
                         eid INTEGER NOT NULL REFERENCES Experiment (eid),
                         rid INTEGER NOT NULL,
                         name varchar(255) NOT NULL,
                         PRIMARY KEY (eid, rid));''')

    def _create_hyperparameter_table(self):
        with self._cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS HyperParameter (
                         eid INTEGER NOT NULL REFERENCES Experiment (eid),
                         rid INTEGER NOT NULL REFERENCES Run (rid),
                         PRIMARY KEY (eid, rid));''')




# This is a PEP 249 compliment database implementation
# taken from the tensorboard dp.py file
class Connection(object):
    """Delegate for PEP 249 Connection object."""

    def __init__(self, delegate):
        """Creates new instance.
        :type delegate: Connection
        """
        self._delegate = delegate
        self._is_closed = False

    def cursor(self):
        """Returns a new database cursor.
        :rtype: Cursor
        """
        return Cursor(self)

    def execute(self, sql, parameters=()):
        """Executes a query and returns its cursor.
        If this is a write query, it won't be executed until the end of the
        transaction.
        This method is not part of PEP 249 but is part of the sqlite3 API.
        :type sql: str
        :type parameters: tuple[object]
        :rtype: Cursor
        """
        cursor = self.cursor()
        cursor.execute(sql, parameters)
        return cursor

    def executemany(self, sql, seq_of_parameters=()):
        """Executes a query many times and returns its cursor.
        If this is a write query, it won't be executed until the end of the
        transaction.
        This method is not part of PEP 249 but is part of the sqlite3 API.
        :type sql: str
        :type seq_of_parameters: list[tuple[object]]
        """
        cursor = self.cursor()
        cursor.executemany(sql, seq_of_parameters)
        return cursor

    def commit(self):
        """Commits transaction."""
        self._check_closed()
        self._delegate.commit()

    def rollback(self):
        """Rolls back transaction."""
        self._check_closed()
        self._delegate.rollback()

    def close(self):
        """Closes resources associated with connection."""
        if self._delegate is not None:
            self._delegate.close()
            self._delegate = None
        self._is_closed = True

    def __enter__(self):
        self._check_closed()
        return self._delegate.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        self._check_closed()
        self._delegate.__exit__(exc_type, exc_value, traceback)

    def _check_closed(self):
        if self._is_closed:
            raise ValueError('connection was closed')


class Cursor(object):
    """Delegate for PEP 249 Cursor object."""

    def __init__(self, connection):
        """Creates new instance.
        :type connection: Connection
        """
        self.connection = connection  # Cycle required by PEP 249
        self._delegate = None  # type: Cursor
        self._is_closed = False

    def execute(self, sql, parameters=()):
        """Executes a single query.
        :type sql: str
        :type parameters: tuple[object]
        """
        self._init_delegate()
        self._delegate.execute(sql, parameters)

    def executemany(self, sql, seq_of_parameters=()):
        """Executes a single query many times.
        :type sql: str
        :type seq_of_parameters: list[tuple[object]]
        """
        self._init_delegate()
        self._delegate.executemany(sql, seq_of_parameters)

    def executescript(self, sql):
        """Executes a script of many queries.
        :type sql: str
        """
        self._init_delegate()
        self._delegate.executescript(sql)

    def fetchone(self):
        """Returns next row in result set.
        :rtype: tuple[object]
        """
        self._check_that_read_query_was_issued()
        return self._delegate.fetchone()

    def fetchmany(self, size=None):
        """Returns next chunk of rows in result set.
        :type size: int
        """
        self._check_that_read_query_was_issued()
        if size is not None:
            return self._delegate.fetchmany(size)
        else:
            return self._delegate.fetchmany()

    def fetchall(self):
        """Returns all remaining rows in the result set.
        :rtype: list[tuple[object]]
        """
        self._check_that_read_query_was_issued()
        return self._delegate.fetchall()

    @property
    def description(self):
        """Returns information about each column in result set.
        See: https://www.python.org/dev/peps/pep-0249/
        :rtype: list[tuple[str, int, int, int, int, int, bool]]
        """
        self._check_that_read_query_was_issued()
        return self._delegate.description

    @property
    def rowcount(self):
        """Returns number of rows retrieved by last read query.
        :rtype: int
        """
        self._check_that_read_query_was_issued()
        return self._delegate.rowcount

    @property
    def lastrowid(self):
        """Returns last row ID.
        :rtype: int
        """
        self._check_that_read_query_was_issued()
        return self._delegate.lastrowid

    def _get_arraysize(self):
        self._init_delegate()
        return self._delegate.arraysize

    def _set_arraysize(self, arraysize):
        self._init_delegate()
        self._delegate.arraysize = arraysize

    arraysize = property(_get_arraysize, _set_arraysize)

    def close(self):
        """Closes resources associated with cursor."""
        if self._delegate is not None:
            self._delegate.close()
            self._delegate = None
        self._is_closed = True

    def __iter__(self):
        """Returns iterator over results of last read query.
        :rtype: types.GeneratorType[tuple[object]]
        """
        self._check_that_read_query_was_issued()
        for row in self._delegate:
            yield row

    def nextset(self):
        """Raises NotImplementedError."""
        raise NotImplementedError('Cursor.nextset not supported')

    def callproc(self, procname, parameters=()):
        """Raises NotImplementedError."""
        raise NotImplementedError('Cursor.callproc not supported')

    def setinputsizes(self, sizes):
        """Raises NotImplementedError."""
        raise NotImplementedError('Cursor.setinputsizes not supported')

    def setoutputsize(self, size, column):
        """Raises NotImplementedError."""
        raise NotImplementedError('Cursor.setoutputsize not supported')

    def _init_delegate(self):
        self._check_closed()
        if self._delegate is None:
            self._delegate = self.connection._delegate.cursor()

    def _check_that_read_query_was_issued(self):
        self._check_closed()
        if self._delegate is None:
            raise ValueError('no read query was issued')

    def _check_closed(self):
        if self._is_closed:
            raise ValueError('cursor was closed')
