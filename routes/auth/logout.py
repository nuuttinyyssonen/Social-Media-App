from flask import Flask, flash, redirect, request, url_for, render_template, Blueprint
from flask_login import login_user, login_user, LoginManager, login_required, logout_user
from Extensions.forms import *
from ...Models.queries import *
from ...Extensions.extensions import login

logout_bp = Blueprint('logout_bp', __name__)

# Logout route for user to logout their account off the session
@logout_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logoutBtn = request.form.get('logout', False)
    # Execute when logoutBtn is clicked
    if logoutBtn != False:
        logout_user()
    return redirect(url_for('login_bp.login'))