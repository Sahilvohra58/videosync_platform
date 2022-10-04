from crypt import methods
from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import logging
import os
import shutil
import sqlite3
import pandas as pd

from utils.speech_to_text import SpeechToText
from utils.validation import Validation
from utils.add_data import populate_data
from utils.produce_video import Produce_Video

from config.config import LoadConfigs


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcript.db'
logging.basicConfig(level=logging.WARNING)

s2t = SpeechToText()
cfg = LoadConfigs()
db = SQLAlchemy(app)

session_data = {}


class Transcript_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Content = db.Column(db.String(5000), nullable=False)
    Start_Time = db.Column(db.Float, nullable=False)
    End_Time = db.Column(db.Float, nullable=False)
    def __repr__(self):
        return f'<Task {self.id}>'


@app.route('/', methods=['GET'])
def home():
    s2t.delete_temp_file()
    for path in ['video_file', 'service_account', 'transcript_file']:
        pth = "uploads/" + path
        os.makedirs(name=pth, exist_ok=True) 
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    try:
        video_file = request.files['video_file']
        json_file = request.files['json_file']
        transcript_file = request.files['transcript_file']

        session_data['VIDEO_FILE_NAME'] = video_file.filename
        session_data['JSON_FILE_NAME'] = json_file.filename
        session_data['TRANSCRIPT_FILE_NAME'] = transcript_file.filename
        
        return Validation(video_file, json_file, transcript_file) \
            .validate_uploaded_files()

    except Exception as E:
        return f"ERROR - {E} - Please try again"

@app.route('/update_subtitles', methods=['GET'])
def update_subtitles():
    transcript = s2t.generate_subtitles(transcript_file_name=session_data.get('TRANSCRIPT_FILE_NAME'))
    populate_data(transcript_dataframe=transcript,
                  Transcript_Data_Class=Transcript_Data,
                  db=db)
    logging.debug(f"transcript.db populated")
    return redirect('/edit_subtitles')

@app.route('/edit_subtitles', methods=['POST', 'GET'])
def edit_subtitles():
    if request.method == 'POST':
        Content = request.form['Content']
        Start_Time = request.form['Start_Time']
        End_Time = request.form['End_Time']
        new_task = Transcript_Data(Content=Content, 
                                    Start_Time=Start_Time,
                                    End_Time=End_Time)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Transcript_Data.query.order_by(Transcript_Data.Start_Time).all()
        return render_template('edit_subtitles_page.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Transcript_Data.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Transcript_Data.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['Content']
        task.start_time = request.form['Start_Time']
        task.end_time = request.form['End_Time']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)

@app.route('/get_transcript', methods=['GET', 'POST'])
def get_transcript():
    temp_transcript_file_path = os.path.join(
        cfg.TEMP_FILES_FOLDER, 
        "transcript.csv")
    if os.path.exists(temp_transcript_file_path):
        return send_file(temp_transcript_file_path, as_attachment=True)
    else:
        return "There was some problem with the download. Please try again."

@app.route('/get_audio_file', methods=['GET', 'POST'])
def get_audio_file():
    temp_audio_file_path = os.path.join(
        cfg.TEMP_FILES_FOLDER, 
        "audio.mp3")
    if os.path.exists(temp_audio_file_path):
        return send_file(temp_audio_file_path, as_attachment=True)
    else:
        return "There was some problem with the download. Please try again."

@app.route('/exit_app', methods=['POST', 'GET'])
def exit_app():
    s2t.delete_temp_file()
    return redirect('/')

@app.route('/produce', methods=['GET', 'POST'])
def produce():
    video_file_path = os.path.join(cfg.UPLOAD_DIRECTORY, "video_file", "video_file.mp4")
    Produce_Video(video_file_name=video_file_path).render_video()

    return send_file(video_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

#/Users/savohra/opt/anaconda3/envs/ai-video-editor/bin/python /Users/savohra/Desktop/testing_upload/app.py
