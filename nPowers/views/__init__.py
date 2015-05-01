from flask import g, render_template, request, jsonify
import requests

from nPowers import app, lm, celery
from nPowers.models import Site, Power, Tag, User
from nPowers.forms import FeedbackForm


_COLLECTION = {'power': Power, 'site': Site}


@lm.user_loader
def load_user(userid):
    return User.objects.with_id(userid)


@celery.task()
def send_mail(to, subject, html):
    url = app.config['MAILGUN_URL']
    auth = ("api", app.config['MAILGUN_KEY'])
    data = {"from": app.config['MAILGUN_USER'],
            "to": to, "subject": subject, "html": html}
    requests.post(url=url, auth=auth, data=data)


@app.route('/')
def index():
    user = g.user
    sites = Site.objects[:20]
    powers = Power.objects[:20]
    tags = Tag.objects[:20]
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


@app.route('/upload', methods=['POST'])
def upload():
    key = request.form['key']
    mode = '?imageView2/2/w/300/h/200'
    data = {
        'status': 'ok',
        'uuid': key.split('/')[1],
        'url': app.config['QINIU_URL'] + key + mode
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
