from flask import Flask, render_template, request
from tables import Table
from crawler import Crawler
from db import Database

app = Flask(__name__)



# @app.route("/")
def template_test():
    kwargs = {"table_name":"Table 1",
              'my_list':['   ','Col1', 'Col2', 'Col3', 'Col4'],
              'fillups': [['Run1', 'test ', 'next'],['Run2','row2', 'row2.5'], ['row3'], ['row4']]}
    return render_template('index.html', **kwargs)


@app.route("/runs")
def runs_in_experiment():
    request.args
    pass

@app.route("/")
def experiments():
    t = Table("Experiment")

    template = {
        "table_name": "Experiments",
        "col_names": t.col_names,
        "rows": t.rows
    }


def main():
    experiments = Crawler().crawl()
    Database.build_database("example.sql", experiments)
    app.run(debug=True)

if __name__ == '__main__':
    main()