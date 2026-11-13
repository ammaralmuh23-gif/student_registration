from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'student_secret_key_2026'

# إعدادات قاعدة البيانات
def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'student_registration'),
        charset='utf8mb4'
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('يجب تسجيل الدخول أولاً', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# --- 1. الواجهة العامة (للطلاب) ---
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        birth_date = request.form['birth_date']
        address = request.form['address']
        phone = request.form['phone']
        grade = request.form['grade']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (full_name, birth_date, address, phone, grade) VALUES (%s, %s, %s, %s, %s)",
            (full_name, birth_date, address, phone, grade)
        )
        conn.commit()
        conn.close()
        
        flash('تم إرسال طلب التسجيل بنجاح، سيتم التواصل معك قريباً', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

# ==========================================
# --- 2. تسجيل دخول المدير ---
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# ==========================================
# --- 3. لوحة تحكم المدير ---
# ==========================================
@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students ORDER BY created_at ASC")
    students = cursor.fetchall()
    conn.close()
    
    # إحصائيات
    total = len(students)
    pending = sum(1 for s in students if s['status'] == 'pending')
    accepted = sum(1 for s in students if s['status'] == 'accepted')
    rejected = sum(1 for s in students if s['status'] == 'rejected')
    
    return render_template('admin/dashboard.html', 
                           students=students,
                           total=total, pending=pending,
                           accepted=accepted, rejected=rejected)

@app.route('/admin/student/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    new_status = request.form['status']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET status = %s WHERE id = %s", (new_status, id))
    conn.commit()
    conn.close()
    flash('تم تحديث حالة الطالب', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/student/<int:id>/delete')
@login_required
def delete_student(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash('تم حذف الطالب', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM admins LIMIT 1")
    admin = cursor.fetchone()
    
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        
        cursor.execute(
            "UPDATE admins SET username = %s, password = %s WHERE id = %s",
            (new_username, new_password, admin['id'])
        )
        conn.commit()
        conn.close()
        
        flash('تم تحديث بيانات المدير بنجاح', 'success')
        return redirect(url_for('admin_profile'))
        
    conn.close()
    return render_template('admin/profile.html', admin=admin)

if __name__ == '__main__':
    app.run(debug=True)