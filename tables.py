from db import Database, Query

class TableI(object):

    @property
    def col_names(self):
        raise NotImplementedError

    @property
    def rows(self):
        raise NotImplementedError


class Table(TableI):

    def __init__(self, table, query=None, order_by=None):
        self._db = Database()
        self._cur = self._db.run_query(table=table, query=query, order_by=order_by)

    @property
    def col_names(self):
        return [name for name, *_ in self._cur.description]

    @property
    def rows(self):
        return iter(self._cur)


class RunTable(TableI):

    def __init__(self, eid, hyperparameter_queries, metric_queries, num_values=100):
        self._db = Database()
        self.eid = eid
        self.metrics_queries = metric_queries
        self.hyperparameter_queries = hyperparameter_queries
        self.hyperparameter_queries.append(Query('eid', '=', eid))
        self.hyperparameters = Table("HyperParameter", hyperparameter_queries)
        self.metrics_curs = [self._db.metric_aggregate(eid, num_values, query) for query in metric_queries]

    @property
    def col_names(self):
        hyperparams_col_names = self.hyperparameters.col_names
        # # inner list comp will return rid, metric
        # metric_col_names = [[name for name, *_ in cur][1] for cur in self.metrics_curs]
        metric_col_names = [q.param for q in self.metrics_queries]
        col_names = hyperparams_col_names[:]
        col_names.extend(metric_col_names)
        return col_names

    @property
    def rows(self):
        return iter(self)

    def __iter__(self):
        rids = {}
        # NOTE RID is the second item in the schema if schema changes this breaks
        for hyper_row in self.hyperparameters.rows:
            hyper_row = list(hyper_row)
            rids[hyper_row[1]] = hyper_row

        # NOTE RID is first index since the metric query only has rid and avg_val
        for metric_cur in self.metrics_curs:
            for metric_row in metric_cur:
                rids[metric_row[0]].append(metric_row[1])

        for row in rids.values():
            yield row
