from app import app, db
from models import User

with app.app_context():
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('dhb571982')
    db.session.add(admin)
    db.session.commit()