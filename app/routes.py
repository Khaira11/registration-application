from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import User, db
from .forms import RegistrationForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('main.register'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('main.success'))
        except Exception as e:
            db.session.rollback()
            flash('Error: Username or email already exists', 'error')
    
    return render_template('register.html', form=form)

@main.route('/success')
def success():
    return render_template('success.html')

@main.route('/users')
def list_users():
    users = User.query.all()
    return render_template('users.html', users=users)
