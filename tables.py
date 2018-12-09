from db import Database, Query
from collections import defaultdict

class TableI(object):

    @property
    def col_names(self):
        raise NotImplementedError

    @property
    def rows(self):
        raise NotImplementedError


class Table(TableI):

    def __init__(self, table, query=None, headings='all', order_by=None):
        self._db = Database()
        self._cur = self._db.run_query(table=table, query=query, headings=headings, order_by=order_by)
        self.headings = headings
        self._rows = []
        self._col_names = []

    @property
    def col_names(self):
        if not self._col_names:
            self._col_names = [name for name, *_ in self._cur.description]
            if self.headings != 'all':
                self._col_names = self.headings
        return self._col_names

    @property
    def rows(self):
        if not self._rows:
            self._rows = list(self._cur)
        return self._rows


class RunTable(TableI):
    # bad design here, ordering matters for the init calls due the way cursors are set up
    # Since the cursor acts as stream (cant be read twice) and running a second query
    # will invalidate the previous
    def __init__(self, eid, hyperparameter_queries, metric_queries, num_values=100):
        self._db = Database()
        self.eid = eid
        self.row_names = self.get_row_names()
        self.metrics_queries = metric_queries
        self.hyperparameter_queries = hyperparameter_queries
        self.hyperparameter_queries.append(Query('eid', '=', eid))
        hyperparam_headings = ['eid', 'rid', *self._db.experiment_hypers[self.eid]]

        self.hyperparameters = Table("HyperParameter", hyperparameter_queries,
                                     headings=hyperparam_headings)
        self.metrics = self.get_metrics(eid)
        self.metric_values = self.get_metric_values(eid, metric_queries, num_values)
        self._rows = []
        self.num_hyper = len(self.hyperparameters.col_names)
        self._col_names = []


    @property
    def col_names(self):
        if not self._col_names:
            hyperparams_col_names = self.hyperparameters.col_names
            # # inner list comp will return rid, metric
            metric_col_names = self.metrics
            # the first col names are eid, dont want this in table
            col_names = hyperparams_col_names[1:]
            col_names.extend(metric_col_names)
            self._col_names = col_names
        return self._col_names

    @property
    def rows(self):
        if not self._rows:
            # have to do a consistency check here\
            rids = defaultdict(list)
            # NOTE RID is the second item in the schema if schema changes this breaks
            for hyper_row in self.hyperparameters.rows:
                hyper_row = list(hyper_row)
                # do not include the eid
                rids[hyper_row[1]].extend(hyper_row[1:])

            # NOTE RID is first index since the metric query only has rid and avg_val
            for metric in self.metric_values:
                for metric_run in metric:
                    rids[metric_run[0]].append(metric_run[1])

            rows = []
            for rid, row in rids.items():
                if len(row) == len(self.col_names):
                    rows.append(row)
            self._rows = rows
        return self._rows

    def get_row_names(self):
        _row_names = {}
        q = self._db.run_query('Run', [Query('eid', '=', self.eid)])
        for _, rid, run_name in q:
            _row_names[rid] = run_name
        return _row_names

    def __iter__(self):
        return self.rows

    def get_metrics(self, eid):
        return self._db.experiment_metrics[eid]

    def get_metric_values(self, eid, metric_queries, num_values):
        queried_metrics = {q.param: q for q in metric_queries}
        metric_rows = []

        for met in self.metrics:
            q = Query(met, 'IS NOT', 'NULL')
            if met in queried_metrics:
                q = queried_metrics[met]
            metric_rows.append(list(self._db.metric_aggregate(eid, num_values, q)))

        return metric_rows

















































