from flask import Flask
from flask.ext.login import LoginManager
from flask_bootstrap import Bootstrap


# import config file
from .config import *


app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SITENAME'] = SITENAME
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


# late import so modules can import their dependencies properly
from .forms import *
from .views import *
from .login import *


@login_manager.user_loader
def load_user(userid):
    return User(uid=userid)
