
from flask import Flask, request, render_template, session, redirect
import bcrypt
import os
import psycopg2
from sql_functions import sql_fetch, sql_write
import boto3
from werkzeug.utils import secure_filename
from datetime import datetime, date
from get_age import get_age
from sleep import format_sleep_time


S3_URL = 'https://growappbucket.s3.ap-southeast-2.amazonaws.com/'
UPLOAD_FOLDER = 'static/images/upload/'



DB_URL = os.environ.get('DATABASE_URL', 'dbname=grow_app')
SECRET_KEY = os.environ.get('SECRET_KEY', 'pretend secret key for testing')

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['AWS_ACCESS_KEY'] = AWS_ACCESS_KEY
app.config['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY





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
            print(password_valid)
            #logs in and sets session data
            if user_email == email and password_valid:
                session['logged_in'] = True
                session['user'] = name
                session['id'] = user_id
                return redirect('/')
            else:
                incorrect_input = True
        
        return render_template('login.html', incorrect_input=incorrect_input)

        

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
        emails = sql_fetch('SELECT email FROM users')
        for db_email in emails:
            if email == db_email[0]:
                email_already_used = True
                return render_template('signup.html', email_already_used=email_already_used)

        if password != check_password:
            no_match = True
            return render_template('signup.html', no_match=no_match)


        if len(name) > 0 and len(email) > 0 and len(password) > 0 and password == check_password:
            #hash the user password for security
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
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
        print(baby)

        return render_template('dashboard.html', baby=baby, get_age=get_age)
    else:
        return redirect('/login')


@app.route('/growth', methods=['GET', 'POST'])
def growth():
    if session.get('logged_in'):
        param_baby_id = request.args.get('baby_id')
        user_id= session['id']
        if request.method == 'GET':
            
            baby = sql_fetch('SELECT baby_id, name, birth_date, height, weight FROM babies WHERE baby_id=%s', [param_baby_id])
        
            return render_template('growth.html', baby=baby )
        if request.method == 'POST':
            height = request.form.get('height')
            weight = request.form.get('weight')
            
            if height != None:
                sql_write('UPDATE babies SET height=%s WHERE baby_id=%s and user_id=%s', [height, param_baby_id, user_id])
                return redirect(f'/growth?baby_id={param_baby_id}')
            
            if weight != None:
                sql_write('UPDATE babies SET weight = %s WHERE baby_id=%s and user_id=%s', [weight, param_baby_id, user_id])
                return redirect(f'/growth?baby_id={param_baby_id}')
    else:
        return redirect('login')


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
            baby_name = sql_fetch('SELECT name FROM babies WHERE baby_id = %s', [param_baby_id])
            print(baby_name)
            
            return render_template('milestones.html', all_milestones=all_milestones,  param_baby_id=param_baby_id, baby_name=baby_name)
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
        user_id = session.get('id')
        param_baby_id = request.args.get('baby_id')
        
        eating_habits = sql_fetch('SELECT date, time_of_day, food_type, eating_habits.baby_id FROM eating_habits INNER JOIN babies ON babies.baby_id=eating_habits.baby_id WHERE eating_habits.baby_id=%s and babies.user_id=%s ORDER BY eating_habits.date, eating_habits.time_of_day DESC LIMIT 1', [param_baby_id, user_id])
        nap_time = sql_fetch('SELECT duration_mins FROM sleeping_habits WHERE baby_id=%s', [param_baby_id])
        nap_start_end = sql_fetch('SELECT nap_start, nap_end FROM sleeping_habits WHERE baby_id=%s ORDER BY date DESC, nap_end DESC LIMIT 1', [param_baby_id])
        
        nap_start, nap_end = format_sleep_time(nap_start_end)


        if len(eating_habits) > 0:
            last_ate = datetime.strptime(eating_habits[0][1], "%H:%M")
            last_ate = last_ate.strftime("%I:%M %p")
        else:
            last_ate = ''
       
        if len(nap_time) > 0:
            total = 0
            for nap in nap_time:
                total += nap[0]
            nap_avg = total / len(nap_time)
            if nap_avg % 60 != 0:
                nap_avg_hrs = str(round(nap_avg / 60, 2))
                hrs_mins_list = nap_avg_hrs.split(".")
                avg_mins = str(round((int(hrs_mins_list[1]) / 100) * 60))
                avg_hrs = str(hrs_mins_list[0])
                nap_avg = avg_hrs + "hr(s) " + avg_mins + "minute(s)"
                return render_template('sleep_food.html', param_baby_id=param_baby_id, eating_habits=eating_habits, nap_avg=nap_avg, nap_start_end=nap_start_end, nap_start=nap_start, nap_end=nap_end, last_ate=last_ate)
            else:
                nap_avg = str(round((total / len(nap_time)) / 60)) + " hour(s)"
                return render_template('sleep_food.html', param_baby_id=param_baby_id, eating_habits=eating_habits, nap_avg=nap_avg, nap_start_end=nap_start_end, nap_start=nap_start, nap_end=nap_end, last_ate=last_ate)
                
        else:
            nap_avg = "No sleep recorded yet"


        
        return render_template('sleep_food.html', param_baby_id=param_baby_id, eating_habits=eating_habits, nap_avg_=nap_avg, nap_start_end=nap_start_end)
    else:
        return redirect('/login')

@app.route('/food_submit_action', methods=["POST"])
def food_submit_action():
    baby_id = request.args.get('baby_id')
    food_type = request.form.get('food_type')
    time_of_day = request.form.get('eat_time')
    date = request.form.get('food_date')
    sql_write('INSERT INTO eating_habits(time_of_day, food_type, baby_id, date) VALUES (%s, %s, %s, %s)', [time_of_day, food_type, baby_id, date])
    return redirect(f'/sleep_food?baby_id={baby_id}')

@app.route('/sleep_submit_action', methods=["POST"])
def sleep_submit_action():
    baby_id = request.args.get('baby_id')
    nap_start = request.form.get('nap_start')
    nap_end = request.form.get('nap_end')
    hours = request.form.get('hours')
    minutes = request.form.get('minutes')
    total_minutes = (int(hours)*60) + int(minutes)
    print(total_minutes)
    date = request.form.get('sleep_date')
    
    sql_write('INSERT INTO sleeping_habits(nap_start, nap_end, duration_mins, baby_id, date) VALUES (%s, %s, %s, %s, %s)', [nap_start, nap_end, total_minutes, baby_id, date])

    
    return redirect(f'/sleep_food?baby_id={baby_id}')



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
            # access the aws s3 storage bucket
            s3_client = boto3.client('s3', aws_access_key_id = AWS_ACCESS_KEY, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
            BUCKET_NAME = 'growappbucket'
            # sets the key to access image
            upload_file_key = str(session['id']) + '_' + session['user'] + '/' + str(baby_id) +  '_baby_id_' + uploaded_image.filename
            s3_client.upload_fileobj(uploaded_image, BUCKET_NAME, upload_file_key)  
            
            profile_picture_url = S3_URL + upload_file_key
            sql_write('UPDATE babies SET profile_picture = %s WHERE baby_id = %s', [profile_picture_url, baby_id])
            if os.path.exists(UPLOAD_FOLDER + uploaded_image.filename):
                os.remove(UPLOAD_FOLDER + uploaded_image.filename)
            
            return redirect('/dashboard')
    else:
        redirect('/login')
 


if __name__ == '__main__':
    app.run(debug=True)