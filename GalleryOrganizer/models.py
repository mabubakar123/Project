from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from GalleryOrganizer import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    images = db.relationship('G_Image', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email}', '{self.image_file}')"

class G_Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(20), nullable=False, default='default.jpg')
    image_actual_name = db.Column(db.String(20), nullable=False, default='default_name.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_class = db.Column(db.String(50), nullable=False)
    image_file_size = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Image('{self.user_id}', '{self.image_name}', '{self.image_actual_name}', '{self.date_posted}', '{self.image_class}', '{self.image_file_size}', '{self.user_id}')"