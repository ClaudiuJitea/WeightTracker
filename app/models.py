from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    height = db.Column(db.Float, nullable=True)  # Height in centimeters
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    weight_entries = db.relationship('WeightEntry', backref='user', lazy='dynamic')
    calorie_entries = db.relationship('CalorieEntry', backref='user', lazy='dynamic')
    weight_goals = db.relationship('WeightGoal', backref='user', lazy='dynamic')
    fasting_sessions = db.relationship('FastingSession', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def make_admin(self):
        self.is_admin = True
    
    def remove_admin(self):
        self.is_admin = False

class WeightEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class WeightGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_weight = db.Column(db.Float, nullable=False)
    target_weight = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    target_date = db.Column(db.DateTime, nullable=False)
    goal_type = db.Column(db.String(20), nullable=False)  # 'steady', 'aggressive', 'moderate', or 'custom'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    completed = db.Column(db.Boolean, default=False)

    @property
    def daily_goal(self):
        total_days = (self.target_date - self.start_date).days
        if total_days <= 0:
            return 0
        total_weight_loss = self.target_weight - self.start_weight
        return total_weight_loss / total_days

    @property
    def weekly_goal(self):
        return self.daily_goal * 7

    @property
    def monthly_goal(self):
        return self.daily_goal * 30

class CalorieEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    protein = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<CalorieEntry {self.food_name} - {self.calories}kcal>'

class FastingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    target_hours = db.Column(db.Integer, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        # For an ongoing fast, ensure duration is not negative due to millisecond race conditions
        delta_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        return max(0, delta_seconds / 3600)

    @property
    def duration_components(self):
        total_seconds = 0
        current_duration_hours = self.duration # Use the existing duration property which handles ongoing fasts correctly
        total_seconds = int(current_duration_hours * 3600)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return {'hours': hours, 'minutes': minutes, 'seconds': seconds, 'raw_hours': current_duration_hours}

    @property
    def progress(self):
        if not self.target_hours:
            return 100
        current_duration = self.duration
        return min(100, (current_duration / self.target_hours) * 100)