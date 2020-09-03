from boa import Boa
from flask import Flask, render_template as flask_render, jsonify, request, redirect

app = Flask(__name__)

# First param is the parent folder of your project.
# In this scenario, it's abs path of __file__ (app.py)
# so that it can find the templates.
boa = Boa(__file__, template_dir = 'html')

@app.route('/', methods = ['GET'])
def index():
	# It's a good practice to not use Boa at all. However, if you're
	# willing to risk yourself, it's nice to specify your request
	# so that you can work with GETs and POSTs. Not needed, though.
	return boa.render('index.html', request, my_ctx_var = 123)
	# This should also work just fine:
	# return boa.render('index.html', my_ctx_var = 123)

if __name__ == '__main__':
	app.run(threaded = True, port = 8000, debug = True)
