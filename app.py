from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import logging
import os

from utils.speech_to_text import SpeechToText
from utils.validation import Validation
from utils.add_data import populate_data
from utils.produce_video import Produce_Video

from config.config import LoadConfigs

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcript.db'
app.config['SECRET_KEY'] = 'supersecretkey'
logging.basicConfig(level=logging.DEBUG)

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
    logging.info(f"Upload path created")
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
        logging.debug(f"Validating uploaded files")
        
        return Validation(video_file, json_file, transcript_file) \
            .validate_uploaded_files()

    except Exception as E:
        logging.error(f"Validation failed due to ERROR - {E}")
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
        Content = request.form['content']
        Start_Time = request.form['start time']
        End_Time = request.form['end time']
        new_task = Transcript_Data(Content=Content, 
                                    Start_Time=Start_Time,
                                    End_Time=End_Time)
        try:
            db.session.add(new_task)
            db.session.commit()
            logging.info(f"Text Added : content = {new_task.Content}, "
                          f"Start_Time = {new_task.Start_Time}, "
                          f"End_Time = {new_task.End_Time}")
            return redirect('/edit_subtitles')
        except Exception as E:
            logging.error(f"ERROR in adding text - {E}")
            return 'There was an issue adding your text'

    else:
        tasks = Transcript_Data.query.order_by(Transcript_Data.Start_Time).all()
        return render_template('edit_subtitles_page.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Transcript_Data.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        logging.info(f"Text deleted : content = {task_to_delete.Content}, "
                      f"Start_Time = {task_to_delete.Start_Time}, "
                      f"End_Time = {task_to_delete.End_Time}")
        return redirect('/edit_subtitles')
    except Exception as E:
        logging.error(f"ERROR in deleting text - {E}")
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Transcript_Data.query.get_or_404(id)

    if request.method == 'POST':
        task.Content = request.form['content']
        task.Start_Time = request.form['start time']
        task.End_Time = request.form['end time']
        try:
            db.session.commit()
            logging.info(f"Text updated : content = {task.Content}, "
                          f"Start_Time = {task.Start_Time}, "
                          f"End_Time = {task.End_Time}")
            return redirect('/edit_subtitles')
        except Exception as E:
            logging.error(f"ERROR in updating text - {E}")
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)

@app.route('/get_transcript', methods=['GET', 'POST'])
def get_transcript():
    temp_transcript_file_path = os.path.join(
        cfg.TEMP_FILES_FOLDER, 
        "transcript.csv")
    if os.path.exists(temp_transcript_file_path):
        logging.info(f"Sending {temp_transcript_file_path} file for download.")
        return send_file(temp_transcript_file_path, as_attachment=True)
    else:
        return "There was some problem with the download. Please try again."

@app.route('/get_audio_file', methods=['GET', 'POST'])
def get_audio_file():
    temp_audio_file_path = os.path.join(
        cfg.TEMP_FILES_FOLDER, 
        "audio.mp3")
    if os.path.exists(temp_audio_file_path):
        logging.info(f"Sending {temp_audio_file_path} file for download.")
        return send_file(temp_audio_file_path, as_attachment=True)
    else:
        return "There was some problem with the download. Please try again."

@app.route('/exit_app', methods=['POST', 'GET'])
def exit_app():
    logging.debug(f"Deleting temp files and exiting")
    s2t.delete_temp_file()
    return redirect('/')

@app.route('/produce', methods=['GET', 'POST'])
def produce():
    video_file_path = os.path.join(cfg.UPLOAD_DIRECTORY, "video_file", "video_file.mp4")
    logging.debug(f"Producing video")
    Produce_Video(video_file_name=video_file_path).render_video()
    logging.debug(f"Downloading video")
    return send_file(video_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
