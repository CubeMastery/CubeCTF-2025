from . import db

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    head_size = db.Column(db.Float)
    is_bald = db.Column(db.Boolean)
    eyesight = db.Column(db.String)
    largest_count = db.Column(db.String)
    favorite_vegetable = db.Column(db.String)
    cosmic_color = db.Column(db.String)
    left_shoes = db.Column(db.Integer)
    mythical_creature = db.Column(db.String)
    
    following = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )