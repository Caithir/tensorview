from flask import Flask, render_template, request
from tables import Table
from crawler import Crawler
from db import Database, Query

app = Flask(__name__)



@app.route("/runs")
def runs_in_experiment():
    # the request will hold the query info
    queries = []
    for param, value in request.args:
        queries.append(Query(param, *value.split("|")))

    t = Table("runs", query=queries)

    template_args = {
        "table_name": "Runs",
        "col_names": t.col_names,
        "rows": t.rows
    }

@app.route("/")
def experiments():
    t = Table("Experiment")

    template_args = {
        "table_name": "Experiments",
        "col_names": t.col_names,
        "rows": t.rows
    }
    return render_template('index.html', **template_args)



def main():
    # will have to do some argparse stuff here to get log dir and the port
    db_name = "tensorview.db"
    port = 6886
    experiments = Crawler().crawl()
    Database.build_database(db_name, experiments)
    app.run(debug=True, port=port)

if __name__ == '__main__':
    main()
