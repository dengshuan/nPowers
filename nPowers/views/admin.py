from uuid import uuid4
from flask import url_for, render_template, Blueprint, request,\
                  redirect, flash, abort
from flask.views import MethodView
from nPowers.models import User, Power, Tag, Site
from nPowers.forms import PowerForm, TagForm, SiteForm, UserForm
from nPowers.utils import admin_required, flash_errors, generate_token

mod = Blueprint('admin', __name__, url_prefix='/admin')

MODEL_FORM = {'tag': (Tag, TagForm),
              'power': (Power, PowerForm),
              'site': (Site, SiteForm),
              'user': (User, UserForm),
              }


class AddView(MethodView):
    decorators = [admin_required]

    def __init__(self, collection, template):
        self.collection = collection
        self.template = template
        self.form = MODEL_FORM[collection][1]

    def get(self):
        CollectionForm = self.form
        form = CollectionForm()
        key = 'uploads/' + str(uuid4())
        policy = {'callbackUrl': 'http://site-powered-by.org/upload',
                  'callbackBody': 'key=$(key)'}
        token = generate_token(key, policy)
        return render_template(self.template, form=form,
                               collection=self.collection,
                               key=key, token=token)

    def post(self):
        CollectionForm = self.form
        form = CollectionForm(request.form)
        if form.validate_on_submit():
            form.save()
            flash('Add successfully!', 'success')
        else:
            flash_errors(form)
        return redirect(url_for('admin.manage', collection=self.collection))


class EditView(MethodView):
    decorators = [admin_required]

    def __init__(self, collection, template):
        self.template = template
        self.collection = collection
        self.model = MODEL_FORM[collection][0]
        self.form = MODEL_FORM[collection][1]

    def get(self, uuid):
        CollectionForm = self.form
        CollectionModel = self.model
        form = CollectionForm()
        key = 'uploads/' + str(uuid4())
        policy = {'callbackUrl': 'http://site-powered-by.org/upload',
                  'callbackBody': 'key=$(key)'}
        token = generate_token(key, policy)
        item = CollectionModel.objects.get_or_404(id=uuid)
        return render_template(self.template, form=form,
                               collection=self.collection,
                               item=item, key=key, token=token)

    def post(self, uuid):
        CollectionForm = self.form
        CollectionModel = self.model
        form = CollectionForm(request.form)
        item = CollectionModel.objects.get_or_404(id=uuid)
        if form.validate_on_submit():
            form.save()
            flash("Update successfully!", 'success')
        else:
            flash_errors(form)
        return redirect(url_for('admin.manage', collection=self.collection))


class DeleteView(MethodView):
    def get(self):
        pass

    def post(self):
        pass

# register url
for collection in MODEL_FORM.keys():
    edit_url = '/edit/' + collection + '/<uuid>'
    add_url = '/add/' + collection
    edit_func = 'edit_' + collection
    add_func = 'add_' + collection
    edit_template = 'admin/edit_' + collection + '.html'
    add_template = 'admin/add_' + collection + '.html'
    mod.add_url_rule(edit_url,
                     view_func=EditView.as_view(
                         edit_func, template=edit_template,
                         collection=collection))
    mod.add_url_rule(add_url,
                     view_func=AddView.as_view(
                         add_func, template=add_template,
                         collection=collection))


@mod.route('/<collection>', defaults={'page': 1})
@mod.route('/<collection>/<int:page>')
@admin_required
def manage(page, collection='site'):
    per_page = 200
    first = per_page * (page - 1)
    last = first + per_page
    if collection in MODEL_FORM.keys():
        CollectionModel = MODEL_FORM[collection][0]
        objects = CollectionModel.objects.order_by('_id')[first:last]
        pagination = CollectionModel.objects.paginate(page=page, per_page=per_page)
        return render_template('admin/base.html',
                               collection=collection, object_list=objects,
                               pagination=pagination)
    else:
        abort(404)
