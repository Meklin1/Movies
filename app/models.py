from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    role = db.Column(db.String(255), nullable=False)
    
    def check_password(self, password):
        # Compare the provided password with the password stored in the database
        return self.password == password

class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    genres = db.Column(db.Text, nullable=False)
    original_language = db.Column(db.String(50), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    popularity = db.Column(db.Float, nullable=False)
    production_companies = db.Column(db.Text)
    release_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(255), nullable=False)
    tagline = db.Column(db.Text)
    vote_average = db.Column(db.Float, nullable=False)
    vote_count = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Text)
    keywords = db.Column(db.Text)
    poster_path = db.Column(db.String(255), nullable=False)
    backdrop_path = db.Column(db.String(255), nullable=False)
    
class Similar_Movies(db.Model):
    __tablename__ = 'similar_movies'
    id = db.Column(db.Integer, primary_key=True)
    similar_ids = db.Column(db.Text, nullable=False)

# class MovieData(db.Model):
#     __tablename__ = 'movie_data'
#     FILMID = db.Column(db.Integer, primary_key=True)
#     TITLE = db.Column(db.Text(255))
#     ADULT = db.Column(db.Boolean)
#     BACKDROP_PATH = db.Column(db.Text(255))
#     ORIGINAL_LANGUAGE = db.Column(db.Text(255))
#     ORIGINAL_TITLE = db.Column(db.Text(255))
#     OVERVIEW = db.Column(db.Text(255))
#     POPULARITY = db.Column(db.Text)
#     POSTER_PATH = db.Column(db.Text(255))
#     RELEASE_DATE = db.Column(db.Text(255))
#     RUNTIME = db.Column(db.Integer)
#     VOTE_AVERAGE = db.Column(db.Text)
#     VOTE_COUNT = db.Column(db.Integer)
#     TAGLINE = db.Column(db.Text(255))
#     COLLECTIONID = db.Column(db.Integer)
#     DIRECTOR_NAME = db.Column(db.Text(255))
#     PRODUCER_NAME = db.Column(db.Text(255))
#     ACTORS = db.Column(db.Text(255))
#     GENRES = db.Column(db.Text(255))