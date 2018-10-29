from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def template_test():
    kwargs = {"my_string":"Table 1",
              'username': 123,
              'my_list':[[1, 1, 'Hi', 'Princess', 9], [5], ['rachel', 89, 2]],
              'fillups': [['   '],['wild', 'this'], ['turtle', 'colter']]}
    return render_template('index.html', **kwargs)

if __name__ == '__main__':
    app.run(debug=True)