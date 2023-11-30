
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()  


app = Flask(__name__)

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
db = SQLAlchemy(app)

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

    def __repr__(self):
        return f'<log {self.birdid}>'

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        new_bird = request.form['bird']
        sighting = Log.query.filter_by(bird=new_bird).first()
        if sighting:
            sighting.sighting_time = datetime.now()
            db.session.commit()
            message = f"{new_bird} sighting updated."
        else:
            new_sighting = Log(bird=new_bird, sighting_time=datetime.now())
            db.session.add(new_sighting)
            db.session.commit()
            message = f"{new_bird} has been sighted."

    bird_sightings = Log.query.order_by(Log.birdid.asc()).all()
    print("Retrieved bird sightings:", bird_sightings)  
    sighted_count = Log.query.filter(Log.sighting_time.isnot(None)).count()
    print("Total number of sightings:", sighted_count)  
    total_bird_count = 745  # Total number of birds that can be sighted
    if bird_sightings:
        print("First sighting:", bird_sightings[0].bird, bird_sightings[0].sighting_time)
    

    return render_template('index.html', bird_sightings=bird_sightings, message=message, sighted_count=sighted_count, total_bird_count=total_bird_count)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, port=5002)

