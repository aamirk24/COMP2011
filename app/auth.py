from flask import Blueprint, flash, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import SignUpForm, LogInForm
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Validating user exists and password entered matches the stored password
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.dashboard'))
        else:
            flash('Invalid email or password.', category='danger')
    return render_template("login.html", form=form, user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Checking if email is already registered
        if user:
            flash("Email already exists.", category='danger')
        else:

            # Creating new user
            new_user = User(
                email = form.email.data,
                first_name = form.first_name.data,
                username = form.username.data,
                password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            )

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully')
            return redirect(url_for('views.dashboard'))

    return render_template('signup.html', form=form, user=current_user)

