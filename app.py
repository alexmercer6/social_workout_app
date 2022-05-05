
from flask import Flask, request, render_template, session, redirect, url_for
import bcrypt
import os
import psycopg2
from sql_functions import sql_fetch, sql_write
import boto3
from werkzeug.utils import secure_filename


S3_URL = 'https://growappbucket.s3.ap-southeast-2.amazonaws.com/'
UPLOAD_FOLDER = 'static/images/upload/'



DB_URL = os.environ.get('DATABASE_URL', 'dbname=grow_app')
SECRET_KEY = os.environ.get('SECRET_KEY', 'pretend secret key for testing')

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_ACCESS_SECRET_KEY = os.environ.get('AWS_ACCESS_SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['AWS_ACCESS_KEY'] = AWS_ACCESS_KEY
app.config['AWS_ACCESS_SECRET_KEY'] = AWS_ACCESS_SECRET_KEY





@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        #retrieve email and password from user input
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        
        #check if they match in the database
        results = sql_fetch('SELECT user_id, name, email, password_hash FROM users')
        for user_id, name, email, password_hash in results:
            #checks if paassword matches the hashed_password
            password_valid = bcrypt.checkpw(user_password.encode(), password_hash.encode())
            #logs in and sets session data
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
        #clears session data and logs the user out
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
            #hash the user password for security
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            print(password)
            #insert new users info into the database
            sql_write('INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)', [name, email, password_hash])
            return redirect('/login')
    
    return render_template('signup.html')
        



@app.route('/dashboard')
def dashboard():
    if session.get('logged_in'):
        user_id = session['id']
        #shows only the logged in user's babies
        baby = sql_fetch('SELECT baby_id, name, birth_date, profile_picture, user_id FROM babies WHERE user_id = %s', [user_id])
        
        return render_template('dashboard.html', baby=baby)
    else:
        return redirect('/login')

@app.route('/milestones', methods=['GET', 'POST'])
def milestones():
    param_baby_id = int(request.args.get('baby_id'))
    
    if request.method == 'GET':
        if session.get('logged_in'):
            user_id = session['id']
            #access milestones table and completed milestone table
            #The LEFT JOIN keyword returns all records from the left table (table1), and the matching records from the right table (table2)
            #will still return the left table if no matches in the right
            #will render the checkbox ticked if matches in the right table
            #unique to each baby
            all_milestones = sql_fetch('SELECT milestones.id, milestone, month_range, completed, baby_id FROM milestones LEFT JOIN completed_milestones ON milestones.id = completed_milestones.milestone_id')
            
            
            return render_template('milestones.html', all_milestones=all_milestones,  param_baby_id=param_baby_id)
        else:
            return redirect('/login')
    
    if request.method == 'POST':
        completed_checklist = request.form.getlist('check_box')
        
        if len(completed_checklist) > 0:
            for id in completed_checklist:
                sql_write('INSERT INTO completed_milestones (completed, milestone_id, baby_id) VALUES (%s, %s, %s )', ['True', id, param_baby_id])
        
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
    if session.get('logged_in'):

        user_id = session['id']
        if request.method == 'POST':
            default_avatar = 'static/images/baby_icon.png'
            name = request.form.get('name')
            birth_date = request.form.get('birthdate')
            split_date = birth_date.split('-')
            split_date.reverse()
            birth_date = '/'.join(split_date)
            print(birth_date)
            sql_write("INSERT INTO babies (name, birth_date, profile_picture, user_id) VALUES (%s, %s, %s, %s)", [name, birth_date, default_avatar, user_id])
            return redirect('/dashboard')
    else:
        return redirect('/login')

@app.route('/sleep_food')
def sleep():
    if session.get('logged_in'):
        param_baby_id = int(request.args.get('baby_id'))
        
        eating_habits = sql_fetch('SELECT date, time_of_day, food_type, baby_id FROM eating_habits ORDER BY date DESC')
        sleeping_habits = sql_fetch('SELECT date, time_of_day, duration, baby_id FROM sleeping_habits ORDER BY date DESC')
        return render_template('sleep_food.html', param_baby_id=param_baby_id, eating_habits=eating_habits, sleeping_habits=sleeping_habits)
    else:
        return redirect('/login')

@app.route('/food_submit_action', methods=["POST"])
def food_submit_action():
    baby_id = request.args.get('baby_id')
    food_type = request.form.get('food_type')
    time_of_day = request.form.get('eat_time')
    date = request.form.get('food_date')
    sql_write('INSERT INTO eating_habits(time_of_day, food_type, baby_id, date) VALUES (%s, %s, %s, %s)', [time_of_day, food_type, baby_id, date])
    return redirect('/sleep_food')

@app.route('/sleep_submit_action', methods=["POST"])
def sleep_submit_action():
    baby_id = request.args.get('baby_id')
    time_of_day = request.form.get('time')
    hours = request.form.get('hours')
    minutes = request.form.get('minutes')
    date = request.form.get('sleep_date')
    duration = str(hours) + 'hr(s) ' + str(minutes) + 'minute(s)'
    sql_write('INSERT INTO sleeping_habits(time_of_day, duration, baby_id, date) VALUES (%s, %s, %s, %s)', [time_of_day, duration, baby_id, date])

    
    return redirect('/sleep_food')



@app.route('/upload_profile_picture', methods=['GET', 'POST'])
def upload():
    if session.get('logged_in'):
        baby_id = request.args.get('baby_id')
        print(baby_id)
        if request.method == 'GET':
            return render_template('profile_picture.html', baby_id=baby_id)

        if request.method == 'POST':
            #gets the image from form input
            uploaded_image = request.files['image']
            #saves the uploaded image to static folder
            # uploaded_image.save(UPLOAD_FOLDER + uploaded_image.filename)
            # UPLOAD_FOLDER + 
            # access the aws s3 storage bucket
            s3_client = boto3.client('s3', aws_access_key_id = AWS_ACCESS_KEY, aws_secret_access_key = AWS_SECRET_KEY)
            BUCKET_NAME = 'growappbucket'
            # sets the key to access image
            upload_file_key = str(session['id']) + '_' + session['user'] + '/' + str(baby_id) +  '_baby_id_' + uploaded_image.filename
            s3_client.upload_file(uploaded_image.filename, BUCKET_NAME, upload_file_key)  
            
            profile_picture_url = S3_URL + upload_file_key
            sql_write('UPDATE babies SET profile_picture = %s WHERE baby_id = %s', [profile_picture_url, baby_id])
            if os.path.exists(UPLOAD_FOLDER + uploaded_image.filename):
                os.remove(UPLOAD_FOLDER + uploaded_image.filename)
            
            return redirect('/dashboard')
    else:
        redirect('/login')
 


if __name__ == '__main__':
    app.run(debug=True)