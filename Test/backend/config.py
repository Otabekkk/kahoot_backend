import secrets

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:ztw02@localhost:5432/kahoot2'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = secrets.token_hex(16)
