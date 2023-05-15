from flask import Blueprint, session, flash, render_template, url_for, redirect
from Extensions.forms import Reset, PasswordReset
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from ...Extensions.extensions import mail, db
from ...Models.models import *
from ...Models.queries import *

reset_bp = Blueprint('reset_bp', __name__)
password_reset_bp = Blueprint('password_reser_bp', __name__)
s = URLSafeTimedSerializer('ThisIsSecret')


# reset route for user to be able to reset password via email
@reset_bp.route('/reset', methods=['GET', 'POST'])
def reset():
    form = Reset()

    # Execute code only if form has data
    if form.validate_on_submit():

        global emailValue
        emailValue = form.email.data
        session['temporaryEmail'] = form.email.data
        token = s.dumps(emailValue, salt='password-reset')
        msg = Message('Password Reset', sender='nuutti.project@gmail.com', recipients=[emailValue])
        link = url_for('password_reset', token=token, _external=True)
        msg.body = 'Your link is {}'.format(link)
        mail.send(msg)
        flash('Message was semt successfully')

    return render_template('./auth/reset.html', form=form)

# Route for password reset when link from email is clicked
@password_reset_bp.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    # Try block to see if the token we are using is still valid meaning has the time expired yet
    try:
        s.loads(token, salt='password-reset', max_age=3600)
    except SignatureExpired:
        return render_template('signatureExpired.html')
    
    form = PasswordReset()
    # Execute code only if form has data
    if form.validate_on_submit():
        user = UserQueries.get_by_email(session['temporaryEmail'])
        if user:
            # if current User is valid then generate new password to it and update the specific db record
            new_password = generate_password_hash(form.password.data)
            User.query.filter_by(email=session['email']).update(dict(password=new_password))
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('noUser.html')
    
    return render_template('./auth/password_reset.html', form=form, token=token)