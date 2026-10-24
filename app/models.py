from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash



class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer,primary_key=True)
    hostname = db.Column(db.String(100),nullable=False)
    ip_address = db.Column(db.String(45),nullable=False, unique=True, index=True)
    prefix_length = db.Column(db.Integer, nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    vendor = db.Column(db.String(100),nullable=False)
    model = db.Column(db.String(100),nullable=True)
    serial_number = db.Column(db.String(100),nullable=True)
    site = db.Column(db.String(100),nullable=True)
    location = db.Column(db.String(100),nullable=True)
    vlan = db.Column(db.String(100),nullable=True)
    purdue_level = db.Column(db.String(10), nullable=False, default="Unassigned")
    zone = db.Column(db.String(100), nullable=False, default="Unassigned")
    status = db.Column(db.String(30),nullable=False,default="active")
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,server_default=db.func.now() , onupdate=db.func.now())

    def __repr__(self):
        return f"<Device {self.hostname} (with IPv4 address: {self.ip_address})>"



class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255),nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256),nullable=False)
    role = db.Column(db.String(20),nullable=False, default="viewer")
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())


    @property
    def is_active(self):
        return self.active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
        


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
