from .models import *
from flask import session

class UserQueries():

    @classmethod
    def get_by_email(cls, email):
        return User.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_id(cls, id):
        return User.query.filter_by(id=id).first()
    
    @classmethod
    def get_by_username(cls, username):
        return User.query.filter_by(username=username).first()
    
    @classmethod
    def exists_by_email(cls, email):
        return db.session.query(db.session.query(User).filter_by(email=email).exists()).scalar()
    
    @classmethod
    def exists_by_username(cls, username):
        return db.session.query(db.session.query(User).filter_by(username=username).exists()).scalar()


class FollowingQueries():

    @classmethod
    def get_by_id(cls, id):
        return Following.query.filter_by(id=id).first()


class FollowersQueries():

    @classmethod
    def get_by_id(cls, id):
        return Followers.query.filter_by(parent_id=id).first()


class ImgQueries():

    @classmethod
    def get_by_id(cls, id):
        return Img.query.filter_by(parent_id=id).first()

    @classmethod
    def get_all_by_id(cls, id):
        return Img.query.filter_by(parent_id=id).all()
    
    @classmethod
    def get_all(cls):
        return Img.query.all()

    @classmethod
    def exists_by_id(cls, id):
        return db.session.query(db.session.query(User).filter_by(id=id).exists()).scalar()


class CommentsQueries():

    @classmethod
    def get_all_by_id(cls, id):
        return Comments.query.filter_by(img_id=id).all()
    
