from flask import Flask, render_template, request
from tables import Table, RunTable
from crawler import Crawler
from db import Database, Query
from util import QueryConverter
import json
import argparse

app = Flask(__name__)

app.url_map.converters['query'] = QueryConverter


@app.route("/runs/<int:eid>/<query:hyperparameter_queries>/<query:metric_queries>")
def runs_in_experiment(eid, hyperparameter_queries, metric_queries):
    # the request will hold the query info
    t = RunTable(eid, hyperparameter_queries=hyperparameter_queries, metric_queries=metric_queries)

    template_args = {
        "table_name": "Runs",
        "headings": t.col_names,
        "table_contents": t.rows,
        "num_hyper_params": t.num_hyper,
        "number_of_cols": len(t.col_names),
        "col_names": json.dumps(t.col_names),
        "eid": eid,
        "run_names": t.row_names,
    }
    return render_template('index.html', **template_args)


@app.route("/runs/<int:eid>/")
def default_runs_in_experiment(eid):
    return runs_in_experiment(eid, [], [])


@app.route("/runs/<int:eid>/<query:hyperparameter_queries>/")
def no_metric_queries_runs_in_experiment(eid, hyperparameter_queries):
    return runs_in_experiment(eid, hyperparameter_queries, [])


@app.route("/")
def landingPage():
    t = Table(table="Experiment")
    rows = t.rows
    eids = []
    number_of_runs = []
    experiment_names = []
    for row in rows:
        experiment_names.append(row[1])
        eids.append(row[0])
        t_for_count = Table('Run', [Query('eid', '=', row[0])])
        number_of_runs.append(len(t_for_count.rows))
    template_args = {
        "experiment_names": experiment_names,
        "number_of_runs": number_of_runs,
        "eid": eids,
    }
    return render_template('landing.html', **template_args)

def main():
    # will have to do some argparse stuff here to get log dir and the port
    # logdir and port come from command line
    db_name = "tensorview.db"
    parser = argparse.ArgumentParser("our program")
    args = parser.parse_args()
    num = args.one
    logdir = args.two
    port = args.three
    # logdir = './test_data'
    # port = 6886

    experiments = Crawler().crawl(logdir)
    Database.build_database(db_name, experiments)
    app.run(debug=True, port=port)


main()
