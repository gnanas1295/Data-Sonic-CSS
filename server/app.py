from flask import Flask
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
oauth = OAuth(app)

from routes import *

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
