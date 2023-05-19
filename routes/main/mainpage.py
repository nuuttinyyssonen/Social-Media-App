from flask import Flask, flash, redirect, request, url_for, render_template, Blueprint
from flask_login import login_user, login_user, LoginManager
from ...Extensions.forms import *
from ...Models.queries import *
from ...Models.models import Comments, Img
from ...Extensions.extensions import login, db
from werkzeug.utils import secure_filename

mainpage_bp = Blueprint('mainpage_bp', __name__)
comments_bp = Blueprint('comments_bp', __name__)

# Route for mainpage which contains most of applications features and links
@mainpage_bp.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    # All the necessary inputs and buttons are below
    upload = request.form.get('submit', False)
    profile = request.form.get('profile', False)
    commentBtn = request.form.get('commentBtn', False)
    commentvalue = request.form.get('comment')
    likeBtn = request.form.get('like', False)
    imageId = request.form.get('imageId')
    explore = request.form.get('explore', False)

    global searchFieldValue
    searchFieldValue = request.form.get('search')
    searchBtn = request.form.get('searchBtn', False)

    following_list = []
    image_list = []
    comments_list = []
    post = ""

    logged_in_user = UserQueries.get_by_email(session['email'])
    logged_in_user_id = logged_in_user.id
    logged_in_user_username = logged_in_user.username

    # users_following = Following.query.filter_by(parent_id=logged_in_user_id).first()
    users_following = FollowingQueries.get_by_id(logged_in_user_id)
    if users_following is not None:
        following_list = users_following.following.split(" ")

    # Looping thourgh all the ids in users following list to be able to display other users posts in logged in user's mainpage
    for id in following_list:
        if len(id) > 0:
            images = ImgQueries.get_all_by_id(id)
            singleImage = ImgQueries.get_by_id(id)
            image_list.append(images)

            if singleImage is not None:
                singleImage_id = singleImage.id
                comments = CommentsQueries.get_all_by_id(singleImage_id)
                comments_list.append(comments)
                post = zip(image_list, comments_list)

    # Comments functionality. Adding comment record to db if button is clicked
    if commentBtn != False:
        addComment = Comments(img_id=imageId, comments=commentvalue, username=logged_in_user_username)
        db.session.add(addComment)
        db.session.commit()

    # Link to explore page
    if explore != False:
        return redirect(url_for("explore_bp.explore"))

    # Upload functionality. Adding img-files to db
    if upload != False:
        pic = request.files['pic']

        if not pic:
            return 'No pic uploaded', 400
    
        description = request.form.get('description')
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype

        db.session.expunge_all()

        img = Img(img=pic.read(), mimetype=mimetype, name=filename, description=description, author=session['email'], user=logged_in_user, likes=0)
        db.session.add(img)
        db.session.commit()

    if profile != False:
        return redirect(url_for('privateProfile_bp.privateProfile', id=logged_in_user_id))
    
    # Searching other users functionality. Checking first to see if user with that field value exists...
    if searchBtn != False:
        exists = UserQueries.exists_by_username(searchFieldValue)

        if logged_in_user.username == searchFieldValue:
            print('you are this user')
            return redirect(url_for('mainpage_bp.mainpage'))
        
        elif exists:
            existing_user = UserQueries.get_by_username(searchFieldValue)
            users_id = existing_user.id
            return redirect(url_for('searchedProfile_bp.singleProfiles', id=users_id))
        
        else:
            flash('User not found!')
            return redirect(url_for('mainpage_bp.mainpage'))
        

    return render_template('./main/mainpage.html', image_list=image_list, post=post)


@comments_bp.route('/comments/<int:id>', methods=['GET', 'POST'])
def comments(id):
    img = Img.query.get(id)
    img.likes += 1
    db.session.commit()
    return redirect(url_for('mainpage_bp.mainpage'))