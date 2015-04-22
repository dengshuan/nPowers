from flask import g, render_template, request, jsonify, url_for
from flask.ext.login import login_required

from nPowers import app, lm, cache
from nPowers.models import Site, Power, Tag, User
from nPowers.forms import FeedbackForm
from nPowers.utils import ImageHandler

@lm.user_loader
def load_user(userid):
    return User.objects.with_id(userid)


@app.route('/')
def index():
    user = g.user
    sites = Site.objects
    powers = Power.objects
    tags = Tag.objects
    return render_template('index.html', sites=sites, powers=powers, tags=tags, user=user)


@app.route('/search')
def search():
    return render_template('coming_soon.html')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        form = FeedbackForm()
    if request.method == 'POST':
        form = FeedbackForm(request.form)
        if form.validate():
            form.save()
    return render_template('feedback.html', form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        handler = ImageHandler(file)
        handler.make_thumbnail(300, 200)
        import os
        filename = os.path.split(handler.thumbnail_path)[1]
        relpath = os.path.join('uploads', filename)
        data = {
            'status': 'ok',
            'id': handler.id,
            'url': url_for('static', filename=relpath)
        }
        return jsonify(data)
