from flask import Flask, render_template, request
from tables import Table
from crawler import Crawler
from db import Database

app = Flask(__name__)



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
    return render_template('index.html', **template_args)



def main():
    experiments = Crawler().crawl()
    Database.build_database("example.sql", experiments)
    app.run(debug=True)

if __name__ == '__main__':
    main()
