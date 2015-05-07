from flask import Flask, g, render_template
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask.ext.login import LoginManager, current_user
from flask.ext.cache import Cache
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.bcrypt import Bcrypt
from flask.ext.mail import Mail
from itsdangerous import URLSafeTimedSerializer
from werkzeug.contrib.fixers import ProxyFix


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('config.py')
app.config.from_envvar('APP_CONFIG_FILE')
app.wsgi_app = ProxyFix(app.wsgi_app)

db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)
lm = LoginManager(app)
cache = Cache(app)
toolbar = DebugToolbarExtension(app)
bcrypt = Bcrypt(app)
mail = Mail(app)


ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@app.before_request
def before_request():
    g.user = current_user


@app.before_first_request
def setup_logging():
    if not app.debug:
        import logging
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401


# late import to avoid cycle import
# import filters
from nPowers.utils import make_celery
from nPowers.utils.filters import get_image, get_ids, tell_square,\
    format_time, url_for_other_page, get_static

app.jinja_env.globals['url_for_other_page'] = url_for_other_page
celery = make_celery(app)

from nPowers.views import user, site, power, admin
from nPowers.views import index, search, feedback

app.register_blueprint(user.mod)
app.register_blueprint(site.mod)
app.register_blueprint(power.mod)
app.register_blueprint(admin.mod)
