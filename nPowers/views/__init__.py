from flask import g, render_template, request, jsonify, url_for
from flask.ext.login import login_required

from nPowers import app, lm
from nPowers.models import Site, Power, Tag, User
from nPowers.forms import FeedbackForm
from nPowers.utils import ImageHandler

_COLLECTION = {'power': Power, 'site': Site}


@lm.user_loader
def load_user(userid):
    return User.objects.with_id(userid)


@app.route('/')
def index():
    user = g.user
    sites = Site.objects
    powers = Power.objects
    tags = Tag.objects
    return render_template('index.html', sites=sites,
                           powers=powers, tags=tags, user=user)


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


@app.route('/<collection>/<item_id>/vote', methods=['POST'])
def vote(collection, item_id):
    cid = int(request.form['cid'])
    v = int(request.form['vote'])
    u = g.user
    w = 0
    if u.is_anonymous():
        w = app.config['WEIGHT'][0]
    elif u.is_authenticated():
        w = app.config['WEIGHT'][1]
        if u.is_staff:
            w = app.config['WEIGHT'][2]
    Model = _COLLECTION.get(collection)
    item = Model.objects.get_or_404(id=item_id)
    item.comments[cid].votes += v * w
    item.save()
    data = {
        'status': 'ok',
        'message': 'vote %s on comment-%s' % (v, cid)
    }
    return jsonify(data)
