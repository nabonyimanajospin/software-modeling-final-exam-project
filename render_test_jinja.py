from jinja2 import Environment, FileSystemLoader, select_autoescape
from types import SimpleNamespace
from datetime import datetime, date

loader = FileSystemLoader('templates')
env = Environment(loader=loader, autoescape=select_autoescape(['html','xml']))
# Provide a stub url_for function for static paths
def url_for_stub(endpoint, filename=None, **kwargs):
    if endpoint == 'static' and filename:
        return '/static/' + filename
    return '/' + endpoint

env.globals['url_for'] = url_for_stub
# Provide minimal Flask-like globals used by base.html
from types import SimpleNamespace as _SN
env.globals['current_user'] = _SN(is_authenticated=False, name='')
env.globals['get_flashed_messages'] = lambda **kw: []

template = env.get_template('student_dashboard.html')

student = SimpleNamespace(photo_url='default_avatar.png', name='Test Student', student_id='S0001', class_name='Grade 1')
grades = [SimpleNamespace(score=95, subject='Math', term='Term 1', created_at=datetime.now()), SimpleNamespace(score=88, subject='English', term='Term 1', created_at=datetime.now())]
attendance = [SimpleNamespace(date=date.today(), status='present', remarks=''), SimpleNamespace(date=date.today(), status='late', remarks='Traffic')]
notifications = [SimpleNamespace(title='Welcome', message='Hi', created_at=datetime.now())]

html = template.render(student=student, grades=grades, attendance=attendance, attendance_percentage=50, notifications=notifications)
print('Rendered length:', len(html))
with open('render_output_jinja.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Wrote render_output_jinja.html')
