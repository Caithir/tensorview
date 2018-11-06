from flask import Flask, render_template
from tables import Table
app = Flask(__name__)


# @app.route("/")
def template_test():
    kwargs = {"table_name":"Table 1",
              'my_list':['   ','Col1', 'Col2', 'Col3', 'Col4'],
              'fillups': [['Run1', 'test ', 'next'],['Run2','row2', 'row2.5'], ['row3'], ['row4']]}
    return render_template('index.html', **kwargs)

@app.route("/")
def index():
    t = Table("example")

    template = {
        "table_name": "Temp example",
        "col_names": t.col_names,
        "rows": t.rows
    }


if __name__ == '__main__':
    app.run(debug=True)