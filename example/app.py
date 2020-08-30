from boa import BoaRenderer as Boa
from flask import Flask, render_template as flask_render, jsonify, request, redirect

app = Flask(__name__)

boa = Boa(__file__)
boa.set_template_dir('.')

@app.route('/')
def index():
    return boa.render('index.html', request, my_ctx_var = 123)

@app.route('/t/')
def template():
    return boa.render('template.html', request, my_ctx_var = 123)
if __name__ == '__main__':
    app.run(threaded = True, port = 8000, debug = True)
