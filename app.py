from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = 'HSAIJWEHRIUHIUFGF92165009DIUFGIFSFG989234R440837047IDSAFF892'

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT python_dasar, web_development, data_science FROM members WHERE id=%s", (session.get('user_id'),))
    user_data = cur.fetchone()
    cur.close()
    user = None
    if session.get('is_logged_in'):
        user = {'name': session.get('name'), 'email': session.get('email'), 'member': session.get('member'), 'courses': { 'python_dasar': user_data.get('python_dasar'), 'web_development': user_data.get('web_development'), 'data_science': user_data.get('data_science') }}
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('is_logged_in'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password_input = request.form.get('password', '')

        if not email or not password_input:
            return render_template('login.html', message="Semua field wajib diisi.")

        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT id, name, email, password, member FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
        finally:
            cur.close()

        if not user:
            return render_template('login.html', message="Email atau password salah.")

        if check_password_hash(user['password'], password_input):
            session['is_logged_in'] = True
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['member'] = user['member']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message="Email atau password salah.")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('is_logged_in'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not all([name, email, password, confirm]):
            return render_template('register.html', message="Semua field wajib diisi.")
        if password != confirm:
            return render_template('register.html', message="Konfirmasi password tidak sama.")

        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                return render_template('register.html', message="Email sudah terdaftar.")

            pwd_hash = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, pwd_hash)
            )
            mysql.connection.commit()

            # Auto-login setelah registrasi (opsional)
            cur.execute("SELECT id, name, email FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
        finally:
            cur.close()

        session['is_logged_in'] = True
        session['user_id'] = user[0] if isinstance(user, tuple) else user['id']
        session['name'] = user[1] if isinstance(user, tuple) else user['name']
        session['email'] = user[2] if isinstance(user, tuple) else user['email']
        session['member'] = 0
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/member-register/<kelas>', methods=['GET', 'POST'])
def member_register(kelas):
    cur = mysql.connection.cursor()
    if not session.get('is_logged_in'):
        return redirect(url_for('login'))

    class_name = kelas.replace('-', ' ').title()

    user = {
        'name': session.get('name'),
        'email': session.get('email'),
        'id': session.get('user_id')
    }

    if request.method == 'POST':
        phone = request.form.get('phone')
        address = request.form.get('address')
        user_id = session.get('user_id')
        
        if session.get('member') == 1:
            if kelas == 'python-dasar':
                cur.execute("UPDATE members SET python_dasar = %s WHERE id = %s", (1, user_id,))
            elif kelas == 'web-development':
                cur.execute("UPDATE members SET web_development = %s WHERE id = %s", (1, user_id,))
            elif kelas == 'data-science':
                cur.execute("UPDATE members SET data_science = %s WHERE id = %s", (1, user_id,))
            else:
                return render_template('member-register.html', user=user, message="Kelas tidak ditemukan")
        else:
            if kelas == 'python-dasar':
                cur.execute("INSERT INTO members (id, python_dasar) VALUES (%s, %s)", (user_id, 1))
            elif kelas == 'web-development':
                cur.execute("INSERT INTO members (id, web_development) VALUES (%s, %s)", (user_id, 1))
            elif kelas == 'data-science':
                cur.execute("INSERT INTO members (id, data_science) VALUES (%s, %s)", (user_id, 1))
            else:
                return render_template('member-register.html', user=user, message="Kelas tidak ditemukan")
        
        cur.execute(
            "UPDATE users SET phone = %s, address = %s, member = %s WHERE id = %s", (phone, address, 1, user_id)
        )
        
        mysql.connection.commit()
        cur.close()
        
        session['member'] = 1

        return render_template('member-register.html', class_name=class_name, user=user, message="Pendaftaran berhasil!")

    return render_template('member-register.html', class_name=class_name, user=user)

@app.route('/my-courses')
def my_courses():
    if not session.get('is_logged_in'):
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    cur.execute(f"SELECT * FROM members WHERE id = %s", (user_id,))
    member_data = cur.fetchone()
    cur.close()

    classes = []
    if member_data:
        if member_data.get('python_dasar') == 1:
            classes.append("Python Dasar")
        if member_data.get('web-development') == 1:
            classes.append("Web Development")
        if member_data.get('data-science') == 1:
            classes.append("Data Science")

    return render_template('my-courses.html', classes=classes)

@app.route('/my-courses/<course>')
def my_course(course):
    if not session.get('is_logged_in'):
        return redirect(url_for('index'))
    user = {
        'name': session.get('name'),
        'email': session.get('email'),
        'id': session.get('user_id')
    }
    if course == 'python-dasar':
        return render_template('python-dasar.html', user=user)
    elif course == 'web-development':
        return render_template('web-development.html', user=user)
    elif course == 'data-science':
        return render_template('data-science.html', user=user)
    else:
        return render_template('index.html', user=user)

@app.route('/logout')
def logout():
    if 'is_logged_in' in session:
        session.pop('is_logged_in', None)
        session.pop('name', None)
        session.pop('email', None)
        
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)