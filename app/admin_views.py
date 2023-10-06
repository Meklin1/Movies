from app import app
from flask import request, redirect, url_for, flash
from app.utilities import insert_movies_from_csv
from app.utilities import create_tables_psql
from app.utilities import write_recommendations_to_psql
import asyncio
import threading
import time
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from app.models import Movies
from app.models import Similar_Movies
from app.models import User
from app import db
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import jsonify
import jwt
from functools import wraps



login = LoginManager(app)

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user is None or current_user.role != 'admin':
            return jsonify({'message': 'Cannot perform that function!'})
        return func(*args, **kwargs)
    return decorated_view

class MyAdminView(AdminIndexView):
    # Access control logic for the entire admin panel
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    # Redirect to login page for inaccessible views
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


    # Menu link for logout
    @expose('/logout', methods=['GET'])
    def logout(self):
        # Implement logout logic here
        logout_user()
        return redirect(url_for('logout', next=request.url)) # Update the URL to the appropriate logout view in your application

    # Menu link for create_tables
    @expose('/create_tables', methods=['GET'])
    def create_tables(self):
        # Implement create_tables logic here
        return redirect(url_for('create_tables'))

    # Menu link for insert_movies
    @expose('/insert_movies', methods=['GET'])
    def insert_movies(self):
        # Implement insert_movies logic here
        return redirect(url_for('insert_movies'))

    # Menu link for insert_similar_movies
    @expose('/insert_similar_movies', methods=['GET'])
    def insert_similar_movies(self):
        # Implement insert_similar_movies logic here
        return redirect(url_for('insert_similar_movies'))



@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))    


admin = Admin(app, index_view=MyAdminView())
admin.add_view(MyModelView(Movies, db.session))
admin.add_view(MyModelView(Similar_Movies, db.session))
admin.add_link(MenuLink(name='Create tables', url='/create_tables', category='Functions'))
admin.add_link(MenuLink(name='Insert similarity matrix', url='/insert_similar_movies/200', category='Functions'))
admin.add_link(MenuLink(name='Insert movies', url='/insert_movies', category='Functions'))
admin.add_link(MenuLink(name='Logout', url='/logout'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            # Display an error message or redirect to an error page
            return "Invalid username or password. Please try again."

        # Log in the user using Flask-Login's login_user function
        login_user(user)

        # Redirect to the admin index page or any other page
        return redirect(url_for('admin.index'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        
        # Check if admin already exists or new user is trying to create an admin
        admin = User.query.filter_by(role='admin').first()
        if admin or role == 'admin':
            return ({'message': 'Admin already exists'})
        
        # Create new user
        new_user = User(username=username, password=password, email=email, role=role, active=True)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful. You can now login.')
        return redirect(url_for('login'))
    
    return '''
        <form method="post">
            <p><input type=text name=username placeholder="Username" required>
            <p><input type=password name=password placeholder="Password" required>
            <p><input type=email name=email placeholder="Email" required>
            <p><input type=text name=role placeholder="Role" required>
            <p><input type=submit value=Sign Up>
        </form>
    '''


@app.route('/create_tables', methods=['GET'])
@login_required
def create_tables():
    if current_user is None or current_user.role != 'admin':
        return jsonify ({'message': 'Cannot perform that function!'})
    create_tables_psql()
    return 'Table created'


@app.route('/insert_movies', methods=['GET'])
@login_required
def insert_movies():
    if current_user is None or current_user.role != 'admin':
        return jsonify ({'message': 'Cannot perform that function!'})
    csv_file_path = r'data\movies_formated.csv'
    insert_movies_from_csv(csv_file_path)
    return 'Movies inserted'


@app.route('/insert_similar_movies/<int:count>', methods=['GET'])
@login_required
def insert_similar_movies(count):
    if current_user is None or current_user.role != 'admin':
        return jsonify ({'message': 'Cannot perform that function!'})
    write_recommendations_to_psql(count)
    return jsonify ({'message': 'Similar movies inserted'})


def sleep_task():
    time.sleep(20)
    print('Finished sleeping')
