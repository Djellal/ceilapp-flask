from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='student')
    # Add relationship to inscriptions
    inscriptions = db.relationship('Inscription', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_student(self):
        return self.role == 'student'

class Inscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numinsc = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    name_ar = db.Column(db.String(250), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(250), nullable=False)
    quality_id = db.Column(db.Integer, db.ForeignKey('student_quality.id'), nullable=False)
    quality = db.relationship('StudentQuality', backref='inscriptions')
    # Add student relationship
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f'<Inscription {self.numinsc}>'

class StudentQuality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    name_ar = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<StudentQuality {self.name}>'