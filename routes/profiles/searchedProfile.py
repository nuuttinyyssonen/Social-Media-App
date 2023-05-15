from flask import redirect, render_template, request, session, url_for, Blueprint
from ...Models.queries import *
from ...Models.models import *
from ...Extensions.uniqueCode import generate_unique_code, rooms
from ...Extensions.extensions import db

searchedProfile_bp = Blueprint('searchedProfile_bp', __name__)

# This route is for if user searches for other users.
@searchedProfile_bp.route('/profile/<int:id>', methods=['GET', 'POST'])
def singleProfiles(id):
    profile = UserQueries.get_by_id(id)
    images = ImgQueries.get_all_by_id(id)
    sessionUser = UserQueries.get_by_email(session['email'])
    sessionUser_id = sessionUser.id

    follower = FollowersQueries.get_by_id(id)
    following = FollowingQueries.get_by_id(sessionUser_id)

    follower_count = follower.followers_count
    following_count = following.following_count
    post_count = len(images)

    following_boolean = False

    followBtn = request.form.get('follow', False)
    messageBtn = request.form.get('message', False)

    print(follower.followers)

    if str(sessionUser_id) in follower.followers:
        following_boolean = True

    if followBtn != False:

        follower.followers_count += 1
        follower.followers += str(sessionUser_id) + " "
        db.session.commit()

        following.following_count += 1
        following.following += str(id) + " "
        db.session.commit()
    
    # This will redirect user to chat page and create new room and generate code for the logged in user and the user he/she searched for
    if messageBtn != False:
        code = generate_unique_code(5)
        session_username = sessionUser.username
        searchedUser_username = profile.username

        # Some of the variables are defined at the start of function and now reused
        roomNumber = ChatRooms(room_code=code, parent_id=sessionUser_id, parent_id2=id, user1=session_username, user2=searchedUser_username)
        db.session.add(roomNumber)
        db.session.commit()
        
        session['room'] = code
        room = code
        rooms[room] = {'members': 0, 'messages': []}
        return redirect(url_for('chat_bp.chat'))

    return render_template('./profiles/singleprofile.html', images=images, profile=profile, post_count=post_count, id=id, follower_count=follower_count, following_count=following_count, following_boolean=following_boolean)