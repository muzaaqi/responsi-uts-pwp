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
    user = None
    user_data = None

    if session.get('is_logged_in'):
        cur = mysql.connection.cursor()
        cur.execute("SELECT python_dasar, web_development, data_science FROM members WHERE id=%s", (session.get('user_id'),))
        user_data = cur.fetchone()
        cur.close()

        if not user_data:
            user_data = {'python_dasar': 0, 'web_development': 0, 'data_science': 0}

        user = {
            'name': session.get('name'),
            'email': session.get('email'),
            'member': session.get('member'),
            'courses': {
                'python_dasar': user_data.get('python_dasar', 0),
                'web_development': user_data.get('web_development', 0),
                'data_science': user_data.get('data_science', 0)
            }
        }

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

    return render_template('register.html', user=None)

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
    
    user = {
        'name': session.get('name'),
        'email': session.get('email'),
        'id': session.get('user_id')
    }

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM members WHERE id = %s", (user_id,))
    member_data = cur.fetchone()
    cur.close()

    classes = []
    if member_data:
        if member_data.get('python_dasar') == 1:
            classes.append({
                "name": "Python Dasar",
                "image": "python.png",
                "modules": 5
            })
        if member_data.get('web_development') == 1:
            classes.append({
                "name": "Web Development",
                "image": "webdev.png",
                "modules": 4
            })
        if member_data.get('data_science') == 1:
            classes.append({
                "name": "Data Science",
                "image": "datasci.png",
                "modules": 6
            })

    return render_template('my-courses.html', classes=classes, user=user)

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
        modules = [
            {
                'title': 'Pengenalan Python',
                'iframe': 'https://www.youtube.com/embed/fmZX-5r0t5E?si=qaaG9W6HXiMB142X',
                'description': 'Materi dimulai dari pengenalan konsep dasar Python, karakteristiknya yang mudah dibaca, dan kegunaannya yang serbaguna, dilanjutkan dengan langkah-langkah persiapan lingkungan seperti instalasi Python dan IDE (Visual Studio Code/PyCharm). Pembahasan inti mencakup semua konsep fundamental, mulai dari variabel, tipe data (integer, float, string, boolean), operator, hingga cara menerima input pengguna dan melakukan konversi tipe data. Video ini juga menjelaskan secara rinci alur kontrol program menggunakan if, elif, else, dan match case, serta konsep perulangan (loops) menggunakan for dan while. Lebih lanjut, dibahas tuntas struktur data penting seperti List (bisa diubah), Tuple (tidak bisa diubah), Dictionary (key-value), dan Set (unik). Konsep-konsep penting lainnya seperti pembuatan fungsi (termasuk parameter, return, dan scope), penanganan error (try-except), dan operasi file (File I/O) juga diajarkan. Sebagai penutup, semua teori ini dipraktikkan dengan membangun tiga studi kasus aplikasi sederhana: kalkulator, permainan tebak angka, dan aplikasi ujian sekolah.'
            }
        ]
        return render_template('python-dasar.html', user=user, modules=modules)
    elif course == 'web-development':
        modules = [
            {
                'title': 'Pengenalan Web Development',
                'iframe': 'https://www.youtube.com/embed/71a2zeC71gk?si=iReslnM5v_42lBw7',
                'description': 'Video ini menyajikan panduan komprehensif yang dirancang khusus untuk pemula yang ingin menguasai proses pembuatan website secara menyeluruh, dari konsep awal hingga publikasi online. Materi ini kemungkinan besar menguraikan tiga pilar utama pengembangan web front-end: HTML untuk membangun struktur dan kerangka dasar halaman web, CSS untuk memberikan gaya, desain visual, dan tata letak agar website terlihat menarik, serta JavaScript dasar untuk menambahkan fungsionalitas dan interaktivitas bagi pengguna. Berbeda dari tutorial biasa, panduan ini tidak berhenti pada penulisan kode saja, tetapi juga melangkah lebih jauh dengan membahas proses akhir yang krusial, yaitu bagaimana cara mengunggah (hosting) file-file website ke server agar dapat di-publish, sehingga hasil akhirnya dapat diakses secara publik melalui internet.'
            }
        ]
        return render_template('web-development.html', user=user, modules=modules)
    elif course == 'data-science':
        modules = [
            {
                'title': 'Pengenalan Data Science',
                'iframe': 'https://www.youtube.com/embed/gDZ6czwuQ18?si=2Eu3NH6nDiw2CDXJ',
                'description': 'Ini adalah panduan komprehensif yang dirancang untuk pemula absolut, mencakup keseluruhan spektrum Data Science dalam satu video maraton. Materi ini kemungkinan besar dimulai dari dasar-dasar Data Science, kemudian beralih ke topik-topik inti seperti berbagai algoritma Machine Learning (termasuk Clustering, Association, dan Ensemble Learning). Video ini tampaknya juga memberikan porsi yang signifikan untuk Deep Learning, membahas konsep-konsep seperti Neural Networks, Perceptrons, Forward Propagation, dan Backpropagation, menjadikannya sumber belajar lengkap dari awal hingga konsep-konsep lanjutan.'
            }
        ]
        return render_template('data-science.html', user=user, modules=modules)
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