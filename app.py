
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
            # Instead of adding a new sighting, display a message that the bird was not found
            message = f"{new_bird} not found in Birdedex."

    bird_sightings = Log.query.order_by(Log.bird_type,Log.bird.asc()).all()
    
    sighted_count = Log.query.filter(Log.sighting_time.isnot(None)).count()
    
    grouped_sightings = {}
    counter = 1
    for sighting in bird_sightings:
        if sighting.bird_type not in grouped_sightings:
            grouped_sightings[sighting.bird_type] = []
        grouped_sightings[sighting.bird_type].append((counter, sighting))
        counter += 1
        
    total_bird_count = 745  # Total number of birds that can be sighted
    
    if bird_sightings:
        print("First sighting:", bird_sightings[0].bird, bird_sightings[0].sighting_time)
    

    return render_template('index.html', 
                           grouped_sightings=grouped_sightings, 
                           message=message, 
                           sighted_count=sighted_count, 
                           total_bird_count=total_bird_count)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, port=5002)

