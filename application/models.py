from .database import db
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(200), nullable=True)
    blogs = db.relationship('Blog', backref='author')

    def follow(self, other_user):
        # self is the current logged in user who follows some other_user
        follow = Follow(follower_id=self.id, followed_id=other_user.id)
        db.session.add(follow)
        db.session.commit()

    def unfollow(self, other_user):
        follow = Follow.query.filter(Follow.follower_id==self.id, Follow.followed_id==other_user.id).one()
        db.session.delete(follow)
        db.session.commit()

    def is_following(self, other_user):
        follow = Follow.query.filter(Follow.follower_id==self.id, Follow.followed_id==other_user.id).first()
        return follow is not None

    # follower list and a following list using joins of User table and FOllow table. Joins on the condition that User table ID attribute is equal to Follower/Followed Id and filter the particular records in follow tables that matches the logged in user's id
    def followers(self):
        return User.query.join(Follow, Follow.follower_id==User.id).filter(Follow.followed_id==self.id).all()
    
    def following(self):
        return User.query.join(Follow, Follow.followed_id==User.id).filter(Follow.follower_id==self.id).all()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)