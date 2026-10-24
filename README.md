# EduTrack - Student Information Tracking System

A web application for managing students, teachers, grades and attendance, built with Flask and SQLite.

## Features

- **Administrator**: create and delete users, send notifications, back up the database
- **Teacher**: enter grades, mark attendance, delete their own grades, download a report
- **Student**: view grades and attendance, upload a profile photo
- Password hashing, role-based access and login sessions

## Project structure

| File / folder | Description |
|---------------|-------------|
| `app.py` | Flask application: routes and database start-up |
| `models.py` | SQLAlchemy models (User, Admin, Teacher, Student, Grade, Attendance, Notification, SystemSettings) |
| `templates/` | HTML pages (login, dashboards, grade entry, attendance) |
| `static/` | Static files; student photos are saved in `static/uploads/` |
| `render_test.py`, `render_test_jinja.py`, `test_libraries.py` | Small helper scripts for checking the templates and libraries |

## Requirements

- Python 3.10 or newer

## How to run

```
python -m venv venv
venv\Scripts\activate          (Linux / macOS: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Open http://localhost:8000 in your browser.

The SQLite database (`instance/edutrack.db`) is created on the first run, together with a default administrator:

| Username | Password |
|----------|----------|
| `admin` | `admin123` |

Log in as the administrator, create teachers and students on the **Manage Users** page, then log in as those users.
Change the default password and set the `SECRET_KEY` environment variable before using the system for real.

## Notes

- Database files, backups and uploaded photos are not stored in this repository.
- Some project files (`models.py`, `enter_grades.html`) were recovered from earlier copies of the project and
  `mark_attendance.html` was rewritten, because they were missing from the folder this repository was made from.
