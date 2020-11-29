from flask import Flask
from flask_cors import CORS, cross_origin
#declare Flask framework
app = Flask(__name__)
#apply cross-site origin to the app(restfulAPI)
CORS(app)