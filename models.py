from sqlalchemy.orm import relationship
from db import db
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from datetime import datetime

class Message(db.Model):
    _tablename_ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    author = Column(String, nullable=False)  # 'user' or 'assistant'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Relación con el usuario
    user = db.relationship('User', back_populates='messages')  # Relación inversa con User

    @classmethod
    def get_all_messages(cls):
        return db.session.query(cls).all()

    @classmethod
    def get_messages_by_user(cls, user_id):
        return db.session.query(cls).filter(cls.user_id == user_id).order_by(cls.id.asc()).all()

   
class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    #users = db.relationship('User', backref='genres', lazy=True)

    def __init__(self, name):
        self.name = name


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    genres = db.relationship('Genre', secondary='user_genres', backref='users', lazy='dynamic')  # Relación many-to-many con Genre
    messages = db.relationship('Message', back_populates='user', lazy=True)  # Relación con los mensajes

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_genres(self):
        return self.genres.all()
    
    
class UserGenre(db.Model):
    __tablename__ = 'user_genres'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), primary_key=True)