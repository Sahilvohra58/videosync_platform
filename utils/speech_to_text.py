import logging
import os
import shutil
from typing import Union, Optional
import moviepy.editor as mp
import pandas as pd
from google.cloud import speech

from config.config import LoadConfigs

cfg = LoadConfigs()


class SpeechToText():
    def __init__(self):
        self.video_file_path = os.path.join(
                cfg.UPLOAD_DIRECTORY, "video_file", "video_file.mp4")

        self.service_account_path = os.path.join(
                    cfg.UPLOAD_DIRECTORY, "service_account", "service_account.json")
        
       

    def connect_google_client(self, service_account_json: Union[dict, str], return_speech_client=False):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json
        try:
            self._speech_client = speech.SpeechClient()
            if return_speech_client:
                return self._speech_client 
            else:
                return True
        except:
            return False
            #raise ConnectionAbortedError("Failed to connect to gcloud console. 
            # Check your internet connection or try again later")
    
    def _api_request(self, audio_file_path: str):
        with open(audio_file_path, 'rb') as f1:
                byte_data_mp3 = f1.read()

        audio_mp3 = speech.RecognitionAudio(content=byte_data_mp3)

        self._speech_client = self.connect_google_client(self.service_account_path, return_speech_client=True)
        
        config_mp3 = speech.RecognitionConfig(
                sample_rate_hertz=cfg.SAMPLE_RATE_HERTZ,
                enable_automatic_punctuation=cfg.ENABLE_AUTOMATIC_PUNCTUATION,
                enable_word_time_offsets=cfg.ENABLE_WORD_TIME_OFFSETS,
                language_code=cfg.LANGUAGE_CODE
            )

        response_standard_mp3 = self._speech_client.recognize(
                                    config=config_mp3,
                                    audio=audio_mp3
                                    )
        
        return response_standard_mp3.results
    
    def _process_transcript(self, results) -> pd.DataFrame:
        transcript_data = pd.DataFrame(columns=['Content', 'Start_Time', 'End_Time'])
        words, start_time_with_count, end_time_with_count, count = ("", 0,0,0)

        for result in results:
            alternative = result.alternatives[0]

            for word_info in alternative.words:
                word = word_info.word
                start_time = word_info.start_time
                end_time = word_info.end_time

                if count == 0:
                    words = word
                    start_time_with_count = start_time
                    count += 1
                
                elif count >= 5:
                    words = words+ " " + word
                    end_time_with_count = end_time
                    append_list = [words, start_time_with_count.total_seconds(), end_time_with_count.total_seconds()]
                    transcript_data.loc[len(transcript_data)] = append_list
                    count = 0
                
                else:
                    words = words + " " + word
                    count += 1

        append_list = [words, start_time_with_count.total_seconds(), self._my_clip.duration] #end_time.total_seconds()]
        transcript_data.loc[len(transcript_data)] = append_list

        return transcript_data
    
    def populate_data(transcript_dataframe: pd.DataFrame, Transcript_Data_Class, db):
        transcript_db_path = './transcript.db'
        if os.path.exists(transcript_db_path):
            os.remove(transcript_db_path)
        db.create_all()
        for _, row in transcript_dataframe.iterrows():
            append_data = Transcript_Data_Class(
                content = row["Content"],
                start_time = float(row["Start_Time"]),
                end_time = float(row['End_Time']),
            )
            db.session.add(append_data)
            db.session.commit()

    def generate_subtitles(self, transcript_file_name: Optional[str] = None):
        self._my_clip = mp.VideoFileClip(self.video_file_path)
        if transcript_file_name:
            extension = transcript_file_name.split(".")[-1]
            if extension == "db":
                path_old, path_new = os.path.join(
                    cfg.UPLOAD_DIRECTORY, 
                    "transcript_file", 
                    f"transcript_file.{extension}"
                ), os.path.join(
                    f"transcript_file.{extension}"
                )
                shutil.copy(path_old, path_new)
                logging.debug(f"Copied {path_old} file to {path_new}")

            if extension in ['csv', 'xlsx']:
                pth = os.path.join(
                    cfg.UPLOAD_DIRECTORY, 
                    "transcript_file", 
                    f"transcript_file.{extension}"
                )
                cols = ["Content" ,'Start_Time', 'End_Time']

                dtype= {'Content': 'str',
                        'Start_Time': 'float',
                        'End_Time': 'float'}

                transcript = pd.read_csv(pth, usecols=cols, dtype=dtype) if extension == 'csv' else pd.read_excel(pth, usecols=cols, dtype=dtype)
                logging.debug(f"Writing {pth} file into transcript.db")    
        
        else:
            

            temp_audio_file_path = os.path.join(
                cfg.TEMP_FILES_FOLDER, 
                 "audio.mp3")
            os.makedirs(cfg.TEMP_FILES_FOLDER, exist_ok=True) 
            self._my_clip.audio.write_audiofile(temp_audio_file_path)

            if os.stat(temp_audio_file_path).st_size / (1024 * 1024) > 10:
                raise Exception("Cannot process audio files more than 10 mb.")
            
            logging.debug("Requesting API")
            results = self._api_request(audio_file_path=temp_audio_file_path)

            logging.debug("Received response. Processing response")
            transcript = self._process_transcript(results=results)
            logging.debug("Data processed")
        
        temp_transcript_file_path = os.path.join(
            cfg.TEMP_FILES_FOLDER, 
            "transcript.csv")
        transcript.to_csv(temp_transcript_file_path, index=False)

        temp_audio_file_path = os.path.join(
            cfg.TEMP_FILES_FOLDER, 
            "audio.mp3")
        if not os.path.exists(temp_audio_file_path):
            self._my_clip.audio.write_audiofile(temp_audio_file_path)

        return transcript

    def delete_temp_file(self):
        shutil.rmtree(cfg.TEMP_FILES_FOLDER, ignore_errors=True)
        shutil.rmtree(cfg.UPLOAD_DIRECTORY, ignore_errors=True)
        if os.path.exists('transcript.db'):
                os.remove('transcript.db')
