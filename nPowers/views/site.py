from datetime import datetime

from flask import url_for, redirect, Blueprint,\
    render_template, flash, request
from flask.ext.login import login_required

from nPowers.models import User, Site, Comment, Power, Tag
from nPowers.forms import SiteForm, CommentForm
from nPowers.utils import flash_errors


mod = Blueprint('site', __name__, url_prefix='/site')


# class SiteView(ListView):
#     def get_template_name(self):
#         return 'site/list.html'

#     def get_objects(self):
#         return Site.objects


# mod.add_url_rule('/', view_func=SiteView.as_view('show_sites'))
@mod.route('/', defaults={'page': 1})
@mod.route('/page/<int:page>')
def show_sites(page):
    per_page = 5
    first = per_page * (page - 1)
    last = first + per_page
    sites = Site.objects.order_by('_id')[first:last]
    pagination = Site.objects.paginate(page=page, per_page=per_page)
    return render_template('site/list.html',
                           sites=sites, pagination=pagination)


@mod.route('/<slug>')
def detail(slug):
    tags = Tag.objects
    form = CommentForm()
    site = Site.objects.get_or_404(slug=slug)
    return render_template('site/detail.html', site=site, form=form, tags=tags)


@mod.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(slug):
    site = Site.objects.get_or_404(slug=slug)
    if request.method == 'GET':
        form = SiteForm()
        item = Site.objects.get_or_404(slug=slug)
        power_ids = [str(t.id) for t in item.powers]
        return render_template('site/edit.html',
                               site=site, form=form,
                               power_ids=power_ids, item=item)
    if request.method == 'POST':
        form = SiteForm(request.form)
        if form.validate_on_submit():
            site = Site.objects.get_or_404(id=form.uuid.data)
            site.name = form.name.data
            site.intro = form.intro.data
            site.url = form.url.data
            if form.img.data:
                site.img = form.img.data
            power_ids = form.powers.data
            for pid in power_ids:
                power = Power.objects.get(id=pid)
                if power in site.powers:
                    continue
                site.powers.append(power)
            site.last_edit = datetime.now()
            site.save()
            flash("Site info update successfully!")
            return redirect(url_for('site.detail', slug=slug))
        else:
            return redirect(url_for('site.edit', slug=slug))


@mod.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'GET':
        form = SiteForm()
        return render_template('site/add.html', form=form)
    if request.method == 'POST':
        form = SiteForm(request.form)
        if form.validate_on_submit():
            name = form.name.data
            url = form.url.data
            intro = form.intro.data
            power_ids = form.powers.data
            last_edit = datetime.now()
            powers = []
            for pid in power_ids:
                power = Power.objects.get_or_404(id=pid)
                powers.append(power)
            site = Site(name=name, url=url, intro=intro, powers=powers,
                        last_edit=last_edit)
            site.save()
            flash("Site {} info add successfully!".format(name))
            return redirect(url_for('site.site', slug=site.slug))
        return redirect(url_for('site.add'))


@mod.route('/comment/<site_id>', methods=['POST'])
@login_required
def comment(site_id):
    site = Site.objects.get_or_404(id=site_id)
    if request.method == 'GET':
        form = CommentForm()
        return render_template('site.detail', slug=site.slug)
    if request.method == 'POST':
        form = CommentForm(request.form)
        if form.validate_on_submit():
            content = form.content.data
            authorid = form.author.data
            if authorid:
                author = User.objects.get(id=authorid)
                comment = Comment(content=content,
                                  author=author,
                                  created=datetime.now())
                site.comments.append(comment)
                site.save()
            flash("Comment on site {} successfully!".format(site.name),
                  'success')
            return redirect(url_for('site.detail', slug=site.slug))
        else:
            flash_errors(form)
            return redirect(url_for('site.detail', slug=site.slug))
