from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def template_test():
    kwargs = {"my_string":"Table 1",
              'my_list':['   ','Col1', 'Col2', 'Col3', 'Col4'],
              'fillups': [['Run1', 'test ', 'next'],['Run2','row2', 'row2.5'], ['row3'], ['row4']]}
    return render_template('index.html', **kwargs)

if __name__ == '__main__':
    app.run(debug=True)