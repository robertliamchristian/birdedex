from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from datetime import datetime
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

load_dotenv()
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#class User(UserMixin, db.Model):
 #   id = db.Column(db.Integer, primary_key=True)
  #  username = db.Column(db.String(80), unique=True, nullable=False)
   # password_hash = db.Column(db.String(128))

class UserSighting(db.Model):
    __tablename__ = 'user_sighting'
    sightingid = db.Column(db.Integer, primary_key=True)
    birdref = db.Column(db.Integer, db.ForeignKey('log.birdid'))
    userid = db.Column(db.Integer, db.ForeignKey('alluser.id'))
    sighting_time = db.Column(db.DateTime, nullable=True)

class User(UserMixin, db.Model):
    __tablename__ = 'alluser'  # Set the new table name here
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    insert_date = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(255))
    is_admin = db.Column(db.String)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class Log(db.Model):
    __tablename__ = 'log'
    birdid = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(255), nullable=False)
    bird = db.Column(db.String(255), nullable=False)
    family = db.Column(db.String(255), nullable=False)
    latin = db.Column(db.String(255), nullable=True)
    flags = db.Column(db.String(255), nullable=True)
    sighting_time = db.Column(db.DateTime, nullable=True)
    bird_type = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('alluser.id'))  

    def __repr__(self):
        return f'<log {self.birdid}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/suggest_birds')
def suggest_birds():
    query = request.args.get('query')
    if not query:
        return jsonify([])  

    matching_birds = Log.query.filter(Log.bird.ilike(f'%{query}%')).all()
    bird_names = [bird.bird for bird in matching_birds]
    return jsonify(bird_names)

@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    message = ""
    anchor_id = ""

    if request.method == 'POST':
        new_bird_name = request.form['bird']
        new_bird = Log.query.filter_by(bird=new_bird_name).first()

        if new_bird:
            existing_sighting = UserSighting.query.filter_by(birdref=new_bird.birdid, userid=current_user.id).first()
            if existing_sighting:
                existing_sighting.sighting_time = datetime.now()
                message = f"{new_bird_name} sighting updated."
                anchor_id = f"bird-{new_bird.birdid}"
            else:
                new_sighting = UserSighting(birdref=new_bird.birdid, userid=current_user.id, sighting_time=datetime.now())
                db.session.add(new_sighting)
                message = f"New sighting of {new_bird_name} added."
                anchor_id = f"bird-{new_bird.birdid}"

            db.session.commit()

    # Get all birds from the Log (master list)
    all_birds = Log.query.order_by(Log.birdid).all()

    # Get the sightings for the current user
    user_sightings = UserSighting.query.filter_by(userid=current_user.id).all()
    user_sightings_dict = {sighting.birdref: sighting for sighting in user_sightings}

    # Combine the master list with the user's sightings
    user_birdedex = {}
    default_bird_type = "Other"  # For birds without a specified type

    for bird in all_birds:
        bird_type = bird.bird_type if bird.bird_type else default_bird_type

        if bird.birdid in user_sightings_dict:
            sighting = user_sightings_dict[bird.birdid]
            bird_entry = (bird.birdid, bird.bird, sighting.sighting_time)
        else:
            bird_entry = (bird.birdid, '???', None)

        if bird_type not in user_birdedex:
            user_birdedex[bird_type] = []

        user_birdedex[bird_type].append(bird_entry)

    sighted_count = len(user_sightings)
    total_bird_count = len(all_birds)

    return render_template('index.html', 
                           user_birdedex=user_birdedex, 
                           message=message, 
                           sighted_count=sighted_count, 
                           total_bird_count=total_bird_count,
                           anchor_id=anchor_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)


