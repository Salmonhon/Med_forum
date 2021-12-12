
from datetime import datetime

from sqlalchemy.orm import backref
from configuration import db

subscribe = db.Table("subscribe",
                    db.Column("follow", db.Integer, db.ForeignKey('author.id'), primary_key=True),
                    db.Column("follower", db.Integer, db.ForeignKey('author.id'), primary_key=True))


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    pswd = db.Column(db.String(100), nullable=False)
    author_news = db.relationship('News', backref='author', lazy=True)
    subscribes = db.relationship("Author", backref="subscribe", lazy=True, secondary=subscribe, primaryjoin=(subscribe.c.follow == id), secondaryjoin=(subscribe.c.follower == id))
    '''backref adds new column in 'News' model, and by using 'author' we can get a user who created this 'News'.'''

    def __repr__(self):
        return 'id:{}, sname:{}, email:{}, pswd:{}'.format(self.id, self.sname, self.email, self.pswd)

class News (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, unique=True)
    intro = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.today)
    # image = db.Column(db.String(20), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __repr__(self):
        return 'id:{}, title:{}, intro:{}, text:{}, author_id:{}'.format(self.id, self.title, self.intro, self.text, self.author_id)

