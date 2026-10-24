from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ==================== USER CLASS (BASE) ====================
class User(UserMixin, db.Model):
    """
    Base User class - matches your Class Diagram
    All users (Admin, Teacher, Student) inherit from this
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'teacher', 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    admin = db.relationship('Admin', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def login(self):
        """Login method from your Class Diagram"""
        self.last_login = datetime.utcnow()
        db.session.commit()
        return True
    
    def logout(self):
        """Logout method from your Class Diagram"""
        return True
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


# ==================== ADMIN CLASS ====================
class Admin(db.Model):
    """
    Admin class - inherits from User (your Class Diagram)
    """
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    admin_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), default='Administration')
    
    def manage_users(self):
        """Manage users method from your Class Diagram"""
        # This is implemented in the routes
        return True
    
    def backup_data(self):
        """Backup data method from your Class Diagram"""
        # This is implemented in the routes
        return True
    
    def __repr__(self):
        return f'<Admin {self.admin_id} - {self.name}>'


# ==================== TEACHER CLASS ====================
class Teacher(db.Model):
    """
    Teacher class - inherits from User (your Class Diagram)
    """
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Relationships
    grades = db.relationship('Grade', backref='teacher', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='teacher', lazy=True, cascade='all, delete-orphan')
    
    def enter_grades(self, student_id, subject, score, term):
        """Enter grades method from your Class Diagram"""
        grade = Grade(
            student_id=student_id,
            teacher_id=self.id,
            subject=subject,
            score=score,
            term=term
        )
        db.session.add(grade)
        db.session.commit()
        return grade
    
    def mark_attendance(self, student_id, date, status):
        """Mark attendance method from your Class Diagram"""
        attendance = Attendance(
            student_id=student_id,
            teacher_id=self.id,
            date=date,
            status=status
        )
        db.session.add(attendance)
        db.session.commit()
        return attendance
    
    def generate_reports(self):
        """Generate reports method from your Class Diagram"""
        return self.grades
    
    def __repr__(self):
        return f'<Teacher {self.teacher_id} - {self.name} ({self.subject})>'


# ==================== STUDENT CLASS ====================
class Student(db.Model):
    """
    Student class - inherits from User (your Class Diagram)
    """
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    parent_phone = db.Column(db.String(20))
    parent_email = db.Column(db.String(120))
    address = db.Column(db.Text)
    photo_url = db.Column(db.String(200), default='default_avatar.png')
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationships
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def view_attendance(self):
        """View attendance method from your Class Diagram"""
        return self.attendances
    
    def view_grades(self):
        """View grades method from your Class Diagram"""
        return self.grades
    
    def get_attendance_percentage(self):
        """Calculate attendance percentage"""
        total = len(self.attendances)
        if total == 0:
            return 0
        present = len([a for a in self.attendances if a.status == 'present'])
        return round((present / total) * 100, 2)
    
    def get_average_grade(self):
        """Calculate average grade"""
        if not self.grades:
            return 0
        total_score = sum([g.score for g in self.grades])
        return round(total_score / len(self.grades), 2)
    
    def __repr__(self):
        return f'<Student {self.student_id} - {self.name} ({self.class_name})>'


# ==================== GRADE CLASS ====================
class Grade(db.Model):
    """
    Grade class from your Class Diagram
    Stores student grades/marks
    """
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    grade_id = db.Column(db.String(20), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    term = db.Column(db.String(50), nullable=False)  # 'Term 1', 'Term 2', 'Term 3'
    max_score = db.Column(db.Float, default=100.0)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Grade, self).__init__(**kwargs)
        if not self.grade_id:
            self.grade_id = f'G{datetime.now().strftime("%Y%m%d%H%M%S")}'
    
    def enter_grades(self, score):
        """Enter grades method from your Class Diagram"""
        self.score = score
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_grades(self):
        """Get grades method from your Class Diagram"""
        return {
            'grade_id': self.grade_id,
            'subject': self.subject,
            'score': self.score,
            'term': self.term,
            'percentage': (self.score / self.max_score) * 100
        }
    
    def get_letter_grade(self):
        """Calculate letter grade"""
        percentage = (self.score / self.max_score) * 100
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def __repr__(self):
        return f'<Grade {self.grade_id} - {self.subject}: {self.score}/{self.max_score}>'


# ==================== ATTENDANCE CLASS ====================
class Attendance(db.Model):
    """
    Attendance class from your Class Diagram
    Tracks student attendance
    """
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(db.String(20), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'present', 'absent', 'late', 'excused'
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Attendance, self).__init__(**kwargs)
        if not self.attendance_id:
            self.attendance_id = f'A{datetime.now().strftime("%Y%m%d%H%M%S")}'
    
    def record_attendance(self, status):
        """Record attendance method from your Class Diagram"""
        self.status = status
        db.session.commit()
    
    def get_attendance(self):
        """Get attendance method from your Class Diagram"""
        return {
            'attendance_id': self.attendance_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'status': self.status,
            'remarks': self.remarks
        }
    
    def __repr__(self):
        return f'<Attendance {self.attendance_id} - {self.date}: {self.status}>'


# ==================== NOTIFICATION CLASS ====================
class Notification(db.Model):
    """
    Notification class for system notifications
    Supports email/SMS notifications as per your Use Case
    """
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    recipient_type = db.Column(db.String(20), nullable=False)  # 'all', 'students', 'teachers', 'parents'
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(20), default='general')  # 'email', 'sms', 'general'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Notification, self).__init__(**kwargs)
        if not self.notification_id:
            self.notification_id = f'N{datetime.now().strftime("%Y%m%d%H%M%S")}'
    
    def __repr__(self):
        return f'<Notification {self.notification_id} - {self.title}>'


# ==================== SYSTEM SETTINGS CLASS ====================
class SystemSettings(db.Model):
    """
    System settings for configuration
    """
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.setting_key}>'