#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 17:15:05 2023

@author: robbiechristian
"""

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure the SQLAlchemy connection to the PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ryqihbzclaqxbz:9d3b7927f6273b5cf588985f67f23e9db4ed5e23562c01a7d2501d1a21ae45f7@ec2-44-213-228-107.compute-1.amazonaws.com:5432/d9un29stbogiu9'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class BirdSighting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bird_name = db.Column(db.String(255), nullable=False)
    sighting_time = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<BirdSighting {self.bird_name}>'

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        new_bird_name = request.form['bird_name']
        # Check if bird is already sighted
        bird_sighting = BirdSighting.query.filter_by(bird_name=new_bird_name).first()
        if bird_sighting:
            # Update sighting time if bird is already sighted
            bird_sighting.sighting_time = datetime.now()
        else:
            # Add new bird sighting
            bird_sighting = BirdSighting(bird_name=new_bird_name, sighting_time=datetime.now())
            db.session.add(bird_sighting)
        db.session.commit()
        message = f"{new_bird_name} has been sighted."

    # Retrieve all bird sightings
    bird_sightings = BirdSighting.query.all()
    sighted_count = BirdSighting.query.count()

    return render_template('index.html', bird_sightings=bird_sightings, message=message, sighted_count=sighted_count)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)
