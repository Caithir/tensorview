from flask import Flask, render_template, request
from tables import Table, RunTable
from crawler import Crawler
from db import Database, Query
from util import QueryConverter

app = Flask(__name__)

app.url_map.converters['query'] = QueryConverter


@app.route("/runs/<eid>/<query:hyperparameter_queries>/<query:metric_queries>")
def runs_in_experiment(eid, hyperparameter_queries, metric_queries):
    # the request will hold the query info
    t = RunTable(eid, hyperparameter_queries=hyperparameter_queries, metric_queries=metric_queries)

    template_args = {
        "table_name": "Runs",
        "headings": t.col_names,
        "table_contents": list(t.rows)
    }
    return render_template('index.html', **template_args)

@app.route("/")
def experiments():
    t = Table(table="Experiment")

    template_args = {
        "table_name": "Experiments",
        "headings": t.col_names,
        "table_contents": list(t.rows)
    }
    return render_template('index.html', **template_args)



def main():
    # will have to do some argparse stuff here to get log dir and the port
    db_name = "tensorview.db"
    logdir = './test_data'
    port = 6886
    update = True
    experiments = {}
    if update:
        experiments = Crawler().crawl(logdir)
    Database.build_database(db_name, experiments, rebuild=update)
    app.run(debug=True, port=port)


main()
