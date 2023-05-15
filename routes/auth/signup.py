from flask import Flask, flash, redirect, request, url_for, render_template, Blueprint
from ...Extensions.forms import *
from ...Models.queries import *
from ...Extensions.extensions import db
from ...Models.models import User

signup_bp = Blueprint('signup_bp', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = Signup()

    # Execute code only if form has data
    if form.validate_on_submit():
        password = form.password.data
        username = form.username.data
        email = form.email.data

        exists_username = UserQueries.exists_by_username(username)
        exists_email = UserQueries.exists_by_email(email)

        # Checking if user already exists in db with username or email
        if exists_username:
            print('This username is already in use!')
            return redirect(url_for('signup'))
        
        if exists_email:
            print('This email is already in use!')
            return redirect('signup')

        newUser = User(username=username, email=email, first_name=form.first_name.data, last_name=form.last_name.data)
        newUser.set_password(password)

        following = Following(user=newUser, following_count=0, following="")
        followers = Followers(user=newUser, followers_count=0, followers="")

        # adding users to db
        db.session.add(newUser, following)
        db.session.commit()
        db.session.add(followers)
        db.session.commit()
        return redirect(url_for('login_bp.login'))
    
    return render_template('./auth/signup.html', form=form)