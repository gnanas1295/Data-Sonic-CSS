from flask import Flask
from authlib.integrations.flask_client import OAuth
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
oauth = OAuth(app)

# Register OAuth with Google
google = oauth.register(
    name='google',
    client_id=app.config['OAUTH_CREDENTIALS']['google']['id'],
    client_secret=app.config['OAUTH_CREDENTIALS']['google']['secret'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    authorize_kwargs=None,
    redirect_uri='http://127.0.0.1:5000/auth/callback',
    token_url='https://accounts.google.com/o/oauth2/token',
    token_params=None,
    token_kwargs=None,
    userinfo_url='https://www.googleapis.com/oauth2/v1/userinfo',
    userinfo_params=None,
    userinfo_kwargs=None,
    client_kwargs={'scope': 'openid profile email'},
)

from routes import *

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
