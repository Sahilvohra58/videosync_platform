import logging
import os
import pandas as pd
import sqlite3
import json
from flask import redirect
from utils.speech_to_text import SpeechToText
from config.config import LoadConfigs


s2t = SpeechToText()
cfg = LoadConfigs()

class Validation():
    def __init__(self, video_file, json_file, transcript_file):
        self.video_file = video_file
        self.json_file = json_file
        self.transcript_file = transcript_file

    def _validate_and_return_transcript(self, extension, path):
        if extension == 'csv':
            transcript = pd.read_csv(path)
        elif extension == 'xlsx':
            transcript = pd.read_excel(path)
        elif extension == 'db':
            con = sqlite3.connect(path)
            transcript = pd.read_sql("""SELECT * FROM transcript__data""", con)
        else:
            raise Exception("Failed to load data")
        
        assert set(list(transcript.columns)) == set(["Content" ,'Start_Time', 'End_Time'])

        if transcript.isna().sum().sum() != 0:
            logging.error(f"Cannot process files with empty cells.")
            raise Exception("Transcript has some empty cells")

        dtype= {'Content': 'str',
                'Start_Time': 'float',
                'End_Time': 'float'}

        transcript = transcript.astype(dtype=dtype)

        return transcript

    def validate_uploaded_files(self):
        if self.video_file:
            video_file_name = self.video_file.filename
            logging.debug(f"Got video file {video_file_name}")
            extension = video_file_name.split(".")[-1]  # os.path.splittext(video_file.filename)

            if extension not in cfg.ALLOWED_VIDEO_EXTENSIONS:
                logging.error(f"Cannot process file other than .mp4 extension - found {extension}")
                return f"Only .mp4 files allowed - found {extension}"

            pth = os.path.join(
                cfg.UPLOAD_DIRECTORY, "video_file", "video_file.mp4"
            )
            self.video_file.save(pth)
            logging.debug(f"Video file saved at {pth}")

        else:
            return "Video file is required"
        
        if self.json_file or self.transcript_file:
            if self.json_file:
                json_file_name = self.json_file.filename
                logging.debug(f"Validating JSON File {json_file_name}")
                extension = json_file_name.split(".")[-1]

                if extension not in cfg.ALLOWED_JSON_EXTENSIONS:
                    return "Only .json files allowed."
                
                pth = os.path.join(
                    cfg.UPLOAD_DIRECTORY, "service_account", "service_account.json"
                    )

                self.json_file.save(pth)
                logging.debug(f"Saved json file {pth}")

                if not s2t.connect_google_client(service_account_json=pth):
                    return "Failed to connect to gcloud console. Check your internet connection or try again with permission enabled."
                logging.debug(f"Connected to Google client")


            if self.transcript_file:
                transcript_file_name = self.transcript_file.filename
                extension = transcript_file_name.split(".")[-1]

                if extension not in cfg.ALLOWED_TRANSCRIPT_EXTENSIONS:
                    return "Only .csv and .xlsx files allowed."
                
                pth = os.path.join(
                    cfg.UPLOAD_DIRECTORY, "transcript_file", f"transcript_file.{extension}"
                    )

                self.transcript_file.save(pth)
                logging.debug(f"Transcript file saved to {pth}")

                try:
                    transcript = self._validate_and_return_transcript(extension=extension, path=pth)
                    logging.debug(f"Transcript file validation successful")   
                    logging.info("Transcript data:")
                    logging.info(transcript)         
                except Exception as E:
                    os.remove(pth)
                    raise Exception(f"Invalid transcript format - {E}")

        else:
            return "Either service account or transcript file required."
            
        return redirect('/update_subtitles')
