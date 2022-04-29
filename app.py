from flask import Flask, request, render_template, session, redirect
import bcrypt
import os
import psycopg2
from sql_functions import sql_fetch, sql_write

DB_URL = os.environ.get('DATABASE_URL', 'dbname=grow_app')
SECRET_KEY = os.environ.get('SECRET_KEY', 'pretend secret key for testing')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        
        results = sql_fetch('SELECT user_id, name, email, password_hash FROM users')
        for user_id, name, email, password_hash in results:
            password_valid = bcrypt.checkpw(user_password.encode(), password_hash.encode())
            if user_email == email and password_valid:
                session['logged_in'] = True
                session['user'] = name

        return redirect('/')

@app.route('/logout')
def logout():
    return render_template('logout.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

 


if __name__ == '__main__':
    app.run(debug=True)