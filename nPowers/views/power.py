from datetime import datetime
from flask import url_for, redirect, Blueprint, request, \
    render_template, flash
from flask.ext.login import login_required

from nPowers.models import Power, Tag, Site, User, Comment
from nPowers.forms import CommentForm
from nPowers.utils import flash_errors

mod = Blueprint('power', __name__, url_prefix='/power')


@mod.route('/<slug>', defaults={'page': 1})
@mod.route('/<slug>/<int:page>')
def detail(slug, page):
    per_page = 30
    first = per_page * (page - 1)
    last = first + per_page
    power = Power.objects.get_or_404(slug=slug)
    sites = Site.objects(powers=power)
    form = CommentForm()
    comments = power.comments[first:last]
    pagination = power.paginate_field('comments', page=page, per_page=per_page)
    return render_template('power/detail.html', power=power, sites=sites,
                           pagination=pagination, comments=comments, form=form)


@mod.route('/tag/<slug>/', defaults={'page': 1})
@mod.route('/tag/<slug>/page/<int:page>')
def tag(slug, page):
    per_page = 9
    tag = Tag.objects.get_or_404(slug=slug)
    first = per_page * (page - 1)
    last = first + per_page
    powers = Power.objects(tags=tag).order_by('_id')[first:last]
    pagination = Power.objects(tags=tag).paginate(page=page, per_page=per_page)
    return render_template('power/tag.html', tag=tag,
                           powers=powers, pagination=pagination)


@mod.route('/tags')
def tags():
    tags = Tag.objects
    return render_template('power/tags.html', tags=tags)


@mod.route('/comment/<power_id>', methods=['POST'])
def comment(power_id):
    power = Power.objects.get_or_404(id=power_id)
    form = CommentForm(request.form)
    if form.validate_on_submit():
        ip = request.remote_addr
        content = form.content.data
        userid = form.userid.data
        username = form.username.data
        if userid:
            user = User.objects.get_or_404(id=userid)
        else:
            user = User(username=username, ip=ip)
            user.save()
        comment = Comment(content=content,
                          author=user,
                          created=datetime.now())
        power.comments.append(comment)
        power.save()
        flash("Comment on power {} successfully!".format(power.name),
              'success')
        return redirect(url_for('power.detail', slug=power.slug))
    else:
        flash_errors(form)
        return redirect(url_for('power.detail', slug=power.slug))
