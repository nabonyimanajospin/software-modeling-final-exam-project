from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Admin, Teacher, Student, Grade, Attendance, Notification
from datetime import datetime, timedelta
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import uuid

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edutrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('backups', exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== ROUTES ====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_users = User.query.count()
    recent_notifications = Notification.query.order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', 
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_users=total_users,
                         notifications=recent_notifications)

@app.route('/admin/manage-users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/create-user', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    role = request.form.get('role')
    
    # Validation
    if User.query.filter_by(username=username).first():
        flash('Username already exists!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Create user
    user = User(
        username=username,
        password=generate_password_hash(password),
        name=name,
        role=role
    )
    db.session.add(user)
    db.session.commit()
    
    # Create role-specific record
    if role == 'teacher':
        teacher = Teacher(
            user_id=user.id,
            teacher_id=f'T{user.id:04d}',
            name=name,
            subject=request.form.get('subject', 'General')
        )
        db.session.add(teacher)
    elif role == 'student':
        student = Student(
            user_id=user.id,
            student_id=f'S{user.id:04d}',
            name=name,
            class_name=request.form.get('class_name', 'Not Assigned')
        )
        db.session.add(student)
    elif role == 'admin':
        admin = Admin(
            user_id=user.id,
            admin_id=f'A{user.id:04d}',
            name=name
        )
        db.session.add(admin)
    
    db.session.commit()
    flash(f'User {username} created successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/delete-user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete your own account!', 'danger')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/backup-database')
@login_required
def backup_database():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'edutrack_backup_{timestamp}.db'
        
        import shutil
        shutil.copy('instance/edutrack.db', f'backups/{backup_filename}')
        
        flash(f'Database backed up: {backup_filename}', 'success')
    except Exception as e:
        flash(f'Backup failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/send-notification', methods=['POST'])
@login_required
def send_notification():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    title = request.form.get('title')
    message = request.form.get('message')
    recipient_type = request.form.get('recipient_type')
    
    notification = Notification(
        title=title,
        message=message,
        recipient_type=recipient_type,
        sender_id=current_user.id
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Notification sent successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# ==================== TEACHER ROUTES ====================

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    students = Student.query.all()
    recent_grades = Grade.query.filter_by(teacher_id=teacher.id).order_by(Grade.created_at.desc()).limit(10).all()
    
    return render_template('teacher_dashboard.html', 
                         teacher=teacher,
                         students=students,
                         recent_grades=recent_grades)

@app.route('/teacher/enter-grades', methods=['GET', 'POST'])
@login_required
def enter_grades():
    if current_user.role != 'teacher':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject = request.form.get('subject')
        score = float(request.form.get('score'))
        term = request.form.get('term')
        
        # Validation
        if score < 0 or score > 100:
            flash('Score must be between 0 and 100!', 'danger')
            return redirect(url_for('enter_grades'))
        
        # Check if subject matches teacher's subject
        if subject.lower() != teacher.subject.lower():
            flash(f'Warning: You are entering grades for {subject}, but you teach {teacher.subject}. Make sure this is correct.', 'warning')
        
        grade = Grade(
            student_id=student_id,
            teacher_id=teacher.id,
            subject=subject,
            score=score,
            term=term
        )
        db.session.add(grade)
        db.session.commit()
        
        flash('Grade entered successfully!', 'success')
        return redirect(url_for('enter_grades'))
    
    students = Student.query.all()
    return render_template('enter_grades.html', students=students, teacher=teacher)

@app.route('/teacher/mark-attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if current_user.role != 'teacher':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get all student IDs and statuses from form
        student_ids = request.form.getlist('student_id')
        statuses = request.form.getlist('status')
        
        for student_id, status in zip(student_ids, statuses):
            # Check if attendance already exists
            existing = Attendance.query.filter_by(student_id=student_id, date=date).first()
            if existing:
                existing.status = status
                existing.teacher_id = teacher.id
            else:
                attendance = Attendance(
                    student_id=student_id,
                    teacher_id=teacher.id,
                    date=date,
                    status=status
                )
                db.session.add(attendance)
        
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('mark_attendance'))
    
    students = Student.query.all()
    today = datetime.now().date()
    return render_template('mark_attendance.html', students=students, today=today, teacher=teacher)

@app.route('/teacher/delete-grade/<int:grade_id>')
@login_required
def delete_grade(grade_id):
    if current_user.role != 'teacher':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    grade = Grade.query.get_or_404(grade_id)
    
    # Verify this grade belongs to this teacher
    if grade.teacher_id != teacher.id:
        flash('You can only delete grades you entered!', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    student_name = grade.student.name
    subject = grade.subject
    
    db.session.delete(grade)
    db.session.commit()
    
    flash(f'Grade for {student_name} in {subject} deleted successfully!', 'success')
    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/generate-report')
@login_required
def generate_teacher_report():
    if current_user.role != 'teacher':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    report_type = request.args.get('type', 'grades')
    
    if report_type == 'grades':
        grades = Grade.query.all()
        data = [{
            'Student ID': g.student.student_id,
            'Student': g.student.name,
            'Subject': g.subject,
            'Score': g.score,
            'Grade': g.get_letter_grade(),
            'Term': g.term,
            'Date': g.created_at.strftime('%Y-%m-%d')
        } for g in grades]
        
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(output, 
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name=f'grades_report_{datetime.now().strftime("%Y%m%d")}.csv')
    
    return redirect(url_for('teacher_dashboard'))

# ==================== STUDENT ROUTES ====================

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    grades = Grade.query.filter_by(student_id=student.id).all()
    attendance = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).limit(30).all()
    
    # Get notifications for students
    notifications = Notification.query.filter(
        (Notification.recipient_type == 'all') | 
        (Notification.recipient_type == 'students')
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    # Calculate attendance percentage
    total_days = len(attendance)
    present_days = len([a for a in attendance if a.status == 'present'])
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    return render_template('student_dashboard.html',
                         student=student,
                         grades=grades,
                         attendance=attendance,
                         attendance_percentage=attendance_percentage,
                         notifications=notifications)

@app.route('/student/upload-photo', methods=['POST'])
@login_required
def upload_photo():
    if current_user.role != 'student':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    if 'photo' not in request.files:
        flash('No file selected!', 'danger')
        return redirect(url_for('student_dashboard'))
    
    file = request.files['photo']
    
    if file.filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('student_dashboard'))
    
    if file and allowed_file(file.filename):
        # Create unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"student_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
        
        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update database
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        # Delete old photo if exists
        if student.photo_url and student.photo_url != 'default_avatar.png':
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], student.photo_url)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except:
                    pass
        
        student.photo_url = filename
        db.session.commit()
        
        flash('Photo uploaded successfully!', 'success')
    else:
        flash('Invalid file type! Only PNG, JPG, JPEG, GIF allowed.', 'danger')
    
    return redirect(url_for('student_dashboard'))

# ==================== INITIALIZE DATABASE ====================

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin123'),
                name='System Administrator',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            
            admin = Admin(
                user_id=admin_user.id,
                admin_id='A0001',
                name='System Administrator'
            )
            db.session.add(admin)
            db.session.commit()
            
            print("Default admin created: username='admin', password='admin123'")

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000)