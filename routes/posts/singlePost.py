from flask import Blueprint, url_for, redirect, render_template, request
from ...Models.queries import *

singlePost_bp = Blueprint('singlePost_bp', __name__)

@singlePost_bp.route('/post/<int:id>', methods=['GET', 'POST'])
def singlePost(id):
    img = ImgQueries.get_by_own_id(id)
    img_comments = img.comments_child
    user = UserQueries.get_by_email(session['email'])
    username = user.username

    commentValue = request.form.get('commentValue')
    commentBtn = request.form.get('submit', False)

    if commentBtn != False:
        addComment = Comments(img_id=id, comments=commentValue, username=username)
        db.session.add(addComment)
        db.session.commit()
        return redirect(url_for('singlePost_bp.singlePost', id=id))

    return render_template('./posts/post.html', img=img, img_comments=img_comments, id=id)