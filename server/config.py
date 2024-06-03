import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'random_secret_key')
    OAUTH_CREDENTIALS = {
        'google': {
            'id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET')
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
