from flask import Blueprint, request, redirect, url_for,\
                  render_template, flash, abort, g
from flask.ext.login import login_user, logout_user

from nPowers import ts
from nPowers.views import send_mail
from nPowers.models import User
from nPowers.forms import LoginForm, RegisterForm, EmailForm, PasswordForm
from nPowers.utils import flash_errors

mod = Blueprint('user', __name__, url_prefix='/u')


@mod.route('/login', methods=['POST', 'GET'])
def login():
    if g.user.is_authenticated():
        return redirect(url_for('user.profile', userid=g.user.id))
    if request.method == 'GET':
        form = LoginForm()
    elif request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate_on_submit():
            user = User.objects.filter(username=form.username.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user)
                flash('Welcome back {}!'.format(user.username), 'success')
                return form.redirect('index')
            else:
                flash('Username or password invalid', 'alert')
        else:
            flash_errors(form)
    return render_template('user/login.html', form=form)


@mod.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        form = RegisterForm()
    elif request.method == 'POST':
        form = RegisterForm(request.form)
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            user = User(username=username, email=email)
            user.hash_password(password)
            user.save()
            subject = "Confirm your email"
            token = ts.dumps(user.email, salt='email-confirm-key')
            confirm_url = url_for('user.confirm_email',
                                  token=token, _external=True)
            html = render_template('email/activate.html',
                                   username=username, confirm_url=confirm_url)
            to = user.email
            send_mail.apply_async((to, subject, html))
            # login_user(user)
            flash('Nice work {}, please check your email to activate your account!'.format(user.username),
                  'success')
            return redirect(url_for('index'))
    return render_template('user/register.html', form=form)


@mod.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt='email-confirm-key', max_age=86400)
    except:
        abort(404)
    user = User.objects.filter(email=email).first_or_404()
    user.activated = True
    user.save()
    return redirect(url_for('user.login'))


@mod.route('/logout')
def logout():
    logout_user()
    flash('Logout successfully!', 'info')
    return redirect(url_for('index'))


@mod.route('/<userid>')
def profile(userid):
    user = User.objects.get_or_404(id=userid)
    return render_template('user/profile.html', user=user)


@mod.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'GET':
        form = EmailForm()
    elif request.method == 'POST':
        form = EmailForm(request.form)
        if form.validate_on_submit():
            user = User.objects.filter(email=form.email.data).first_or_404()
            subject = "Password reset requested"
            token = ts.dumps(user.email, salt='recover-key')
            recover_url = url_for('user.reset_with_token',
                                  token=token, _external=True)
            html = render_template('email/recover.html',
                                   recover_url=recover_url)
            to = user.email
            send_mail.apply_async((to, subject, html))
            return redirect(url_for('user.login'))
    return render_template('user/reset.html', form=form)


@mod.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt='recover-key', max_age=86400)
    except:
        abort(404)
    if request.method == 'GET':
        form = PasswordForm()
    elif request.method == 'POST':
        form = PasswordForm(request.form)
        if form.validate_on_submit():
            user = User.objects.filter(email=email).first_or_404()
            user.hash_password(form.password.data)
            user.save()
            return redirect(url_for('index'))
    return render_template('user/reset_with_token.html',
                           form=form, token=token)
