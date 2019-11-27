from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='kjksfjklaskflaskfjklasjflk2312'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from shop import routes
from shop.dashboard import routes