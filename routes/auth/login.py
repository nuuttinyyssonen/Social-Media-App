from flask import Flask, flash, redirect, request, url_for, render_template, Blueprint
from werkzeug.urls import url_parse
from flask_login import login_user, login_user, LoginManager
from ...Extensions.forms import *
from ...Models.queries import *
from ...Extensions.extensions import login
from ...Models.models import User

login_bp = Blueprint('login_bp', __name__)
login.login_view = 'login'

@login.user_loader
def load_user(id):
  return User.query.get(int(id))


# Login route to query specific user
@login_bp.route('/', methods=['GET', 'POST'])
def login():
    form = Login()
    # Execute only if form has data to submit
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = UserQueries.get_by_email(email)
        session['email'] = request.form.get('email')
        exists_email = UserQueries.exists_by_email(email)

        # Edge cases if user does not pass correct email or password
        if exists_email != True:
            print('Invalid Email')
            return redirect(url_for('login_bp.login'))

        # Another one
        if user is None or not user.check_password(password):
            print('Invalid Password or Email')
            return redirect(url_for('login_bp.login'))
        
        user_id = user.id
        login_user(user)
        next_page = request.args.get('next')

        # Redirecting user to nextpage
        if not next_page or url_parse(next_page).netloc != '':
            # next_page = url_for('mainpage_bp.mainpage')
            next_page = '/mainpage'
        return redirect(next_page)
    
    return render_template('./auth/login.html', form=form)