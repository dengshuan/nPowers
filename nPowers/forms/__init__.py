from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SelectMultipleField,\
    HiddenField, BooleanField, PasswordField
from wtforms.validators import Required, URL, EqualTo, Email

from nPowers.models import User, Power, Tag, Site, Feedback
from nPowers.utils.validators import Unique


class CommentForm(Form):
    content = TextAreaField(validators=[Required()])
    author = TextField(validators=[Required()])


class PowerForm(Form):
    choices = [(str(t.id), t.name) for t in Tag.objects]
    uuid = HiddenField()
    name = TextField(validators=[Required()])
    intro = TextAreaField()
    url = TextField(validators=[Required(), URL()])
    img = HiddenField()
    tags = SelectMultipleField(choices=choices)

    def save(self):
        if self.uuid.data:
            power = Power.objects.get_or_404(id=self.uuid.data)
        else:
            power = Power()
        power.name = self.name.data
        power.intro = self.intro.data
        power.url = self.url.data
        power.img = self.img.data
        power.tags = []
        for tid in self.tags.data:
            tag = Tag.objects.get_or_404(id=tid)
            power.tags.append(tag)
        power.save()


class TagForm(Form):
    uuid = HiddenField()
    name = TextField(validators=[Required()])

    def save(self):
        if self.uuid.data:
            tag = Tag.objects.get_or_404(id=self.uuid.data)
        else:
            tag = Tag()
        tag.name = self.name.data
        tag.save()


class SiteForm(Form):
    choices = [(str(p.id), p.name) for p in Power.objects]
    uuid = HiddenField()
    name = TextField(validators=[Required()])
    intro = TextAreaField()
    img = HiddenField()
    url = TextField(validators=[Required(), URL()])
    powers = SelectMultipleField(choices=choices)

    def save(self):
        if self.uuid.data:
            site = Site.objects.get_or_404(id=self.uuid.data)
        else:
            site = Site()
        site.name = self.name.data
        site.intro = self.intro.data
        if self.img.data:
            site.img = self.img.data
        site.url = self.url.data
        site.powers = []
        for pid in self.powers.data:
            power = Power.objects.get_or_404(id=pid)
            site.powers.append(power)
        site.save()


class UserForm(Form):
    uuid = HiddenField()
    username = TextField(validators=[Required()])
    is_staff = BooleanField()
    email = TextField(validators=[Email()])
    password = PasswordField(validators=[Required()])
    password_confirm = PasswordField(validators=[EqualTo('password')])

    def save(self):
        if self.uuid.data:
            user = User.objects.get_or_404(id=self.uuid.data)
        else:
            user = User()
        user.username = self.username.data
        user.is_staff = self.is_staff.data
        user.password = self.password.data
        user.save()


class FeedbackForm(Form):
    username = TextField(validators=[Required()])
    email = TextField(validators=[Required()])
    content = TextAreaField(validators=[Required()])

    def save(self):
        feedback = Feedback()
        feedback.username = self.username.data
        feedback.email = self.email.data
        feedback.content = self.content.data
        feedback.save()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class LoginForm(RedirectForm):
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required()])


class RegisterForm(Form):
    username = TextField(validators=[Required(),
                                     Unique(User, User.username, message='Username exists!')])
    email = TextField(validators=[Required(), Email(),
                                  Unique(User, User.email,
                                         message='There is already an account with this email.')])
    password = PasswordField(validators=[Required()])
    confirm = PasswordField(validators=[Required(),
                                        EqualTo('password', message='Passwords must match')])


class EmailForm(Form):
    email = TextField(validators=[Required(), Email()])


class PasswordForm(Form):
    password = PasswordField(validators=[Required()])
