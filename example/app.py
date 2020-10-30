from boa import Boa
from flask import Flask, request, session

app = Flask(__name__)

# First param is the parent directory of your project,
# so that it can find your templates and components.
boa = Boa(__file__, template_dir = 'html')

@app.route('/', methods = ['GET'])
def index():
	# It's a good practice to not use Boa at all. However, if you're
	# willing to risk it, it's nice to specify your request and your session
	# so that you can work with GETs and POSTs and whatever. Not needed, though.
	return boa.render('index.html', request, session, my_ctx_var = 123)
	# This should also work just fine:
	# return boa.render('index.html', my_ctx_var = 123)

if __name__ == '__main__':
	app.run(threaded = True, port = 8000, debug = True)
