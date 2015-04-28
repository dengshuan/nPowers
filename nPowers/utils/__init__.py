import os
from math import ceil
from functools import wraps
from PIL import Image
from uuid import uuid4
from celery import Celery
from flask import request, url_for, render_template,\
    flash, g, abort, redirect
from flask.views import View


from nPowers import app
from nPowers.models import User


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    user = User.objects.get(username=username)
    if user and user.verify_password(password):
        return user.is_staff
    else:
        return False


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error in the %s field - %s" % (
                getattr(form, field).label.text, error),
                  "alert")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user.is_authenticated():
            next_url = request.path
            login_url = '%s?next=%s' % (url_for('user.login'), next_url)
            return redirect(login_url)
        elif g.user.is_staff:
            return f(*args, **kwargs)
        else:
            abort(401)
    return decorated


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


class ListView(View):
    def get_template_name(self):
        raise NotImplementedError()

    def render_template(self, context):
        return render_template(self.get_template_name(), **context)


class ImageHandler:
    UPLOAD_DIR = app.config['UPLOAD_DIR']

    def __init__(self, file, fmt='png'):
        self.img = Image.open(file)
        self.id = str(uuid4())
        self.width, self.height = self.img.size
        self.fmt = fmt

    def _make_path(self, type):
        file_name = '{}_{}.{}'.format(self.id, type, self.fmt)
        return os.path.join(self.UPLOAD_DIR, file_name)

    @property
    def thumbnail_path(self):
        return self._make_path('thumbnail')

    @property
    def resized_path(self):
        return self._make_path('resized')

    def resize(self, width=None, height=None):
        if not(width or height):
            width, height = 400, 300
        elif width and not height:
            ratio = width / self.width
            height = self.height * ratio
            width, height = int(width), int(height)
        elif height and not width:
            ratio = height / self.height
            width = self.width * ratio
            width, height = int(width), int(height)
        else:
            width, height = int(width), int(height)
        im = self.img.resize(width, height)
        resized_file = self._make_path('resized')
        im.save(resized_file, self.fmt)

    def make_thumbnail(self, width, height):
        size = (int(width), int(height))
        self.img.convert(mode='RGB')
        self.img.thumbnail(size)
        thumbnail_file = self._make_path('thumbnail')
        self.img.save(thumbnail_file, self.fmt)


class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count) / float(self.per_page))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages+1):
            if num <= left_edge or \
               (num > self.page - left_current - 1) and \
               num < self.page + right_current or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
