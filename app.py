# from flask import Flask, render_template
#
# app = Flask(__name__)
#
#
# # @app.route('/')
# # def hello_world():
# #     return 'TEST if it works'
#
# @app.route('/')
# def table():
#     return render_template('index.html', )
#
# if __name__ == '__main__':
#     app.run()
#
# from flask import Flask, render_template
# app = Flask(__name__)
#
#
# @app.route("/")
# def template_test():
#     return render_template('index.html', my_string="Wheeeee!", my_list=[0,1,2,3,4,5])
#
#
# # if __name__ == '__main__':
# #     app.run(debug=True)
#
# from jinja2 import Template
# t = Template("Hello {{ something }}!")
# t.render(something="World")
#
#
# t = Template("My favorite numbers: {% for n in range(1,10) %}{{n}} " "{% endfor %}")
# t.render()
