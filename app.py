from flask import Flask, render_template, flash, redirect, url_for, request
from flask import session
from datetime import timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from flask_babel import Babel
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager, babel, migrate
from models import User
from forms import LoginForm, RegistrationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'ar'
app.config['SECRET_KEY'] = 'DhB@571982'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Add these debug configurations
app.config['DEBUG'] = True  # Enable debug mode
app.config['SQLALCHEMY_ECHO'] = True  # Print SQL queries to console
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
babel.init_app(app)
migrate.init_app(app, db)

login_manager.login_view = 'login'
login_manager.login_message = 'الرجاء تسجيل الدخول للوصول إلى هذه الصفحة'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logger.debug(f'Authenticated user {current_user.username} attempting to access login page')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        logger.info(f'Login attempt for email: {form.email.data}')
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            logger.info(f'Successful login for user: {user.username}')
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('home'))
        logger.warning(f'Failed login attempt for email: {form.email.data}')
        flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data, 
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء التسجيل. الرجاء المحاولة مرة أخرى', 'error')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():  # function name matches the endpoint used in url_for('home')
    return render_template('index.html')
from functools import wraps
from flask import abort

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role:
                flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Example of protected route for admin only
@app.route('/users')
@login_required
@role_required('admin')
def users():
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    if role_filter:
        query = query.filter(User.role == role_filter)
        
    users_list = query.all()
    return render_template('users.html', 
                         users=users_list, 
                         search=search, 
                         current_role=role_filter)

# Example of protected route for students
@app.route('/student-dashboard')
@login_required
@role_required('student')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/set-session')
def set_session():
    session['test'] = 'test value'
    return 'Session value set. <a href="/check-session">Check session</a>'
    
@app.route('/check-session')
def check_session():
    return f"Session contains: {session.get('test', 'No value found')}"

@app.route('/debug-csrf')
def debug_csrf():
    return {
        'has_csrf_token': 'csrf_token' in session,
        'session_keys': list(session.keys())
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)