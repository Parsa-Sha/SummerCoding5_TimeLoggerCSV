from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import csv
import os

app = Flask(__name__)
app.secret_key = '5e8d5c66f9c1382c9c291c6ef617f7e613529caca0de24e8b6fe0a6b' 

# Use an absolute path for the CSV file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'time_logs.csv')

def get_last_status():
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            if rows:
                return rows[-1][2]  # Return the status of the last row
    return 'stop'  # Default to 'stop' if no records exist

def get_today_total(day):
    today = datetime.now().date()
    total_time = timedelta()
    start_time = None

    # Adding Day Modifyer
    today = datetime.now().date() + timedelta(day)

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                date = datetime.strptime(row[0], "%Y-%m-%d").date()
                if date == today:
                    if row[2] == 'start':
                        start_time = datetime.strptime(f"{row[0]} {row[1]}", "%Y-%m-%d %H:%M:%S")
                    elif row[2] == 'stop' and start_time:
                        stop_time = datetime.strptime(f"{row[0]} {row[1]}", "%Y-%m-%d %H:%M:%S")
                        total_time += stop_time - start_time
                        start_time = None

    return str(total_time).split('.')[0]  # Remove microseconds

def get_day_name(days_ago):
    return (datetime.now() - timedelta(days=days_ago)).strftime('%A')

def check_credentials(username, password):
    with open('users.csv', 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) >= 2 and row[0] == username and row[1] == password:
                return True
    return False

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']  # Assuming you're using email as username
        password = request.form['password']
        
        if check_credentials(username, password):
            # Login successful
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to dashboard or home page
        else:
            # Login failed
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['email']  # Assuming you're using email as username
        password = request.form['password']
        
        path = os.path.join(BASE_DIR, 'users.csv')
        with open(path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])
    
    return render_template('signup.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        last_status = get_last_status()
        new_status = 'stop' if last_status == 'start' else 'start'
        
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, time, new_status])

        return redirect(url_for('index'))

    current_status = get_last_status()
    button_text = 'Stop' if current_status == 'start' else 'Start'
    button_class = 'stop' if current_status == 'start' else 'start'
    total_time = get_today_total(0)
    
    day0 = total_time
    day1 = get_today_total(-1)
    day2 = get_today_total(-2)
    day3 = get_today_total(-3)
    day4 = get_today_total(-4)
    day5 = get_today_total(-5)
    day6 = get_today_total(-6)

    day2_name = get_day_name(2)
    day3_name = get_day_name(3)
    day4_name = get_day_name(4)
    day5_name = get_day_name(5)
    day6_name = get_day_name(6)

    return render_template('index.html', 
                       day0=day0, day1=day1, day2=day2, day3=day3, day4=day4, day5=day5, day6=day6,
                       day2_name=day2_name, day3_name=day3_name, day4_name=day4_name, day5_name=day5_name, day6_name=day6_name,
                       total_time=total_time, button_class=button_class, button_text=button_text)

if __name__ == '__main__':
    app.run(debug=True)
