from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = 'HSAIJWEHRIUHIUFGF92165009DIUFGIFSFG989234R440837047IDSAFF892'

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

@app.route('/')
def index():
    user = None
    if session.get('is_logged_in'):
        user = [session['name'], session['email']]
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            return render_template('login.html', message="All fields are required.")
        
        query = "SELECT * FROM users WHERE email=%s AND password=%s"
        cur.execute(query, (email, password))
        user = cur.fetchone()

        if user:
            session['is_logged_in'] = True
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['email'] = user[2]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message="Invalid email or password.")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'is_logged_in' in session:
        session.pop('is_logged_in', None)
        session.pop('name', None)
        session.pop('email', None)
        
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)