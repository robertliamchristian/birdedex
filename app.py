from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Read the CSV file into a DataFrame
df = pd.read_csv('birdedex1.csv')

# Create a dictionary to store bird sightings
bird_sightings = {bird: None for bird in df['Bird']}

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        new_bird = request.form['bird_name']
        if new_bird in bird_sightings:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bird_sightings[new_bird] = current_time
        else:
            message = "That bird is not in the dataset. Try again."
    
    sighted_count = sum(1 for time in bird_sightings.values() if time is not None)
    total_count = len(bird_sightings)
    
    return render_template('index.html', bird_sightings=bird_sightings, message=message, sighted_count=sighted_count, total_count=total_count)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
