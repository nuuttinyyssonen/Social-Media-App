from flask import Blueprint, session, render_template
from ...Models.queries import *

chatInbox_bp = Blueprint('chatInbox_bp', __name__)

# Route to see all the user's chats and links for specific chats
@chatInbox_bp.route('/chat/inbox', methods=['GET', 'POST'])
def chatInbox():
    user = UserQueries.get_by_email(session['email'])
    user_id = user.id
    chats = ChatRooms.query.filter_by(parent_id=user_id).all()
    more_chats = ChatRooms.query.filter_by(parent_id2=user_id).all()
    return render_template('./chat/chatInbox.html', chats=chats, more_chats=more_chats)