from app import app
from flask import render_template
from types import SimpleNamespace
from datetime import datetime, date

# Create sample context objects
student = SimpleNamespace(photo_url='default_avatar.png', name='Test Student', student_id='S0001', class_name='Grade 1')
grades = [SimpleNamespace(score=95, subject='Math', term='Term 1', created_at=datetime.now()), SimpleNamespace(score=88, subject='English', term='Term 1', created_at=datetime.now())]
attendance = [SimpleNamespace(date=date.today(), status='present', remarks=''), SimpleNamespace(date=date.today(), status='late', remarks='Traffic')]
notifications = [SimpleNamespace(title='Welcome', message='Hi', created_at=datetime.now())]

with app.test_request_context('/student/dashboard'):
    html = render_template('student_dashboard.html', student=student, grades=grades, attendance=attendance, attendance_percentage=50, notifications=notifications)
    print('Rendered length:', len(html))
    # Optionally write to temp file
    with open('render_output.html','w', encoding='utf-8') as f:
        f.write(html)
    print('Wrote render_output.html')
