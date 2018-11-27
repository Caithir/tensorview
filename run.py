from flask import Flask, render_template, request
app = Flask(__name__)


@app.route("/", methods=['Get', 'Post'])
def template_test():
    kwargs = {"table_name": "Table 1",
              'headings': ['   ','Col1', 'Col2', 'Col3', 'Col4'],
              'table_contents': [['Run1', 0, 12, "test", "turtle"],['Run2','row2', 'row2.5', '23', 'open'], ['row3', '12', 0, 0, 9], ['row4', 21, 't', 12, '9']],
              'results': request.form}
    return render_template('index.html', **kwargs)


# @app.route('/result',methods = ['POST', 'GET'])
# def result():
#    if request.method == 'POST':
#       result = request.form
#       return render_template("result.html",result = result)


if __name__ == '__main__':
    app.run(debug=True)



