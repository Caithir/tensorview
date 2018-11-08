import contextlib
import sqlite3
from collections import namedtuple


class Database(object):

    def __init__(self, db_filename):
        self._conn = Connection(sqlite3.connect(db_filename))

    def _cursor(self):
        return contextlib.closing(self._conn.cursor())

    def parse_logdir_output(self, logdir_kwargs):
        self.create_tables_from_logdir(logdir_kwargs)
        self.populate_tables_from_logdir(logdir_kwargs)

    def create_tables_from_logdir(self, table_schema):
        pass

    def populate_tables_from_logdir(self, logdir_kwargs):
        pass

    def create_hardcoded_table(self):
        with self._cursor() as c:
            c.execute('''\
            CREATE TABLE IF NOT EXISTS EXAMPLE (
            rid INTEGER PRIMARY KEY,
            lr INTEGER,
            arc STRING)
            ''')

            c.execute('''\
            INSERT INTO EXAMPLE VALUES (1, 5, "res"), (2, 111, "MLP"), (4,111, "ERG")''')

    def get_example(self):
        result_cursor = self._conn.execute('''\
        SELECT * FROM example''')
        return result_cursor

    def run_query(self, table, contraints=tuple(['1', '=', '1'])):
        query = f'''SELECT * FROM {table}
                    WHERE {"".join([str(param)+str(comp)+str(value)
                    for param, comp, value in contraints])}'''
        return self._conn.execute(query)



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
