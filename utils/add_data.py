from flask import Flask
from app import db, Transcript_Data, app
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcript.db'

@app.before_first_request
def populate_data(transcript_data: pd.DataFrame):
    transcript_db_path = 'transcript.db'
    if os.path.exists(transcript_db_path):
        os.remove(transcript_db_path)
    db.create_all()
    for _, row in transcript_data.iterrows():
        append_data = Transcript_Data(
            content = row["Words"],
            start_time = float(row["Start time"]),
            end_time = float(row['End time']),
        )
        db.session.add(append_data)
        db.session.commit()