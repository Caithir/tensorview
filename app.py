from flask import Flask, render_template
from tables import Table
app = Flask(__name__)


@app.route("/")
def index():
    t = Table("example")

    template_args = {
        "table_name": "Temp example",
        "col_names":  t.col_names,
        "rows": t.rows
    }
    return render_template('index.html', **template_args)


# @app.route("/query")
def query(POST):
    print(POST)
    index()

if __name__ == '__main__':
    app.run(debug=True)
