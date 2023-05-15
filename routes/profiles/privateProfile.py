from flask import Blueprint, session, render_template, redirect, url_for, request
from ...Models.queries import *

privateProfile_bp = Blueprint('privateProfile_bp', __name__)

# Route for logged in user's profile
@privateProfile_bp.route('/privateProfile/<int:id>', methods=['GET', 'POST'])
def privateProfile(id):
    logged_in_user = UserQueries.get_by_email(session['email'])
    logged_in_user_id = logged_in_user.id
    logged_in_user_username = logged_in_user.username
    logged_in_user_first_name = logged_in_user.first_name
    logged_in_user_last_name = logged_in_user.last_name

    deleteBtn = request.form.get('deleteBtn', False)
    if deleteBtn != False:
        return redirect(url_for('delete'))

    followers = FollowersQueries.get_by_id(logged_in_user_id)
    followers_count = followers.followers_count

    following = FollowingQueries.get_by_id(logged_in_user_id)
    following_count = following.following_count

    images = ImgQueries.get_all_by_id(id)
    post_count = (len(images))
    return render_template('./profiles/profile.html', images=images, post_count=post_count, followers_count=followers_count, following_count=following_count, username=logged_in_user_username, logged_in_user_first_name=logged_in_user_first_name, logged_in_user_last_name=logged_in_user_last_name)