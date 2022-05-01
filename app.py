from crypt import methods
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
                session['id'] = user_id

        return redirect('/')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'GET':
        return render_template('logout.html')
    
    if request.method == 'POST':
        session.clear()
        return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':

        return render_template('signup.html')
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        check_password = request.form.get('check_password')

        if len(name) > 0 and len(email) > 0 and len(password) > 0 and password == check_password:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            print(password)
            sql_write('INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)', [name, email, password_hash])
            return redirect('/login')
    
    return render_template('signup.html')
        



@app.route('/dashboard')
def dashboard():
    if session.get('logged_in'):
        user_id = session['id']
        baby = sql_fetch('SELECT baby_id, name, birth_date, user_id FROM babies WHERE user_id = %s', [user_id])
        
        return render_template('dashboard.html', baby=baby)
    else:
        return redirect('/login')

@app.route('/milestones', methods=['GET', 'POST'])
def milestones():
    baby_id = request.args.get('baby_id')
    print(baby_id)
    if request.method == 'GET':
        if session.get('logged_in'):
            user_id = session['id']
            
            all_milestones = sql_fetch('SELECT milestones.id, milestone, month_range, completed FROM milestones LEFT JOIN completed_milestones ON milestones.id = completed_milestones.milestone_id')
            
            
            return render_template('milestones.html', all_milestones=all_milestones,  baby_id=baby_id)
        else:
            return redirect('/login')
    
    if request.method == 'POST':
        completed_checklist = request.form.getlist('check_box')
        # print(completed_checklist)
        #how to access baby idea hmmm
        
        print(baby_id)
        if len(completed_checklist) > 0:
            for id in completed_checklist:
                sql_write('INSERT INTO completed_milestones (completed, milestone_id, baby_id) VALUES (%s, %s, %s )', ['True', id, baby_id])
        
            return redirect('/dashboard')
        else:
            return redirect('/dashboard')
            

# @app.route('/update_database_action', methods=['POST'])
# def update_database_action():
#     completed_checklist = request.form.getlist('check_box')
#     print(completed_checklist)
#     #how to access baby idea hmmm
#     for id in completed_checklist:
#         sql_write('INSERT INTO milestones_completed (completed, milestone_id, baby_id) VALUES (%s, %s, %s, )', ['True', id,  ])
    
#     return redirect('/milestones')


@app.route('/add_baby', methods=['GET', 'POST'])
def add_baby():
    if request.method == 'GET':
        return render_template('add_baby.html')
 


if __name__ == '__main__':
    app.run(debug=True)