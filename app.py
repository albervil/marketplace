import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://albv:mysecretpassword@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

if 'APP_SECRET' in os.environ:
    app.config['JWT_SECRET_KEY'] = os.environ['APP_SECRET']
else:
    # Just a random string to run the application e.g. locally
    app.config['JWT_SECRET_KEY'] = os.urandom(12)

from views import *


if __name__ == '__main__':
    from populate import populatedb

    populatedb()
    app.run(debug=True)
