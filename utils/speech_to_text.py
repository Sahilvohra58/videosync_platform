from argparse import ArgumentError
import os
import shutil
from typing import Union, Optional
from google.cloud import speech
import moviepy.editor as mp
import pandas as pd
from utils.caching import Cache
from config.config import Load_Configs
from utils.add_data import populate_data


che = Cache()
cfg = Load_Configs()

class Speech_To_Text():
    def __init__(self):
        pass
    def connect_google_client(self, service_account_json: Union[dict, str]):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json
        try:
            self._speech_client = speech.SpeechClient()
        except:
            raise ConnectionAbortedError("Failed to connect to gcloud console. Check your internet connection or try again later")

    def _api_request(self, audio_file_path: str, service_account_json: Union[dict, str]):
        with open(audio_file_path, 'rb') as f1:
                byte_data_mp3 = f1.read()

        self.connect_google_client(service_account_json=service_account_json)

        audio_mp3 = speech.RecognitionAudio(content=byte_data_mp3)

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
        transcript_data = pd.DataFrame(columns=['Words', 'Start time', 'End time'])
        words, start_time_with_count, end_time_with_count, count = ("", 0,0,0)

        for result in results:
            alternative = result.alternatives[0]
            # print("Transcript: {}".format(alternative.transcript))
            # print("Confidence: {}".format(alternative.confidence))

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
    
    def _check_if_transcript_exist(self):
        transcript_file_path1 = os.path.join("./additional_files", self.video_file_name.split('.')[0] + "_transcript.csv")
        transcript_file_path2 = os.path.join("./temp_files", self.video_file_name.split('.')[0] + "_transcript.csv")
        if os.path.exists(transcript_file_path1):
            return transcript_file_path1
        elif os.path.exists(transcript_file_path2):
            return transcript_file_path2
        else: 
            return None


    def delete_temp_file(self,
                            keep_audio_file: Optional[bool] = False,
                            keep_transcript_file: Optional[bool] = False):

        shutil.rmtree('temp_files', ignore_errors=True)
        audio_file_path = os.path.join("additional_files", self.video_file_name.split('.')[0] + "_audio.mp3")
        transcript_file_path = os.path.join("additional_files", self.video_file_name.split('.')[0] + "_transcript.csv")
        if not keep_audio_file:
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)

        if not keep_transcript_file:
            if os.path.exists(transcript_file_path):
                os.remove(transcript_file_path)
    

    def generate_subtitles(self, video_file_name: str,
                            service_account_json: Optional[Union[dict, str]] = None,
                            transcript_file_path: Optional[str] = None,
                            keep_audio_file: Optional[bool] = False,
                            keep_transcript_file: Optional[bool] = False):

        self._my_clip = mp.VideoFileClip(video_file_name)
        self.video_file_name = video_file_name

        if transcript_file_path == None:
            transcript_file_path = self._check_if_transcript_exist()

        if transcript_file_path == None:
            if service_account_json is None:
                raise ArgumentError("Service account credentials required to connect with gcloud console if transcript is not provided.")
            duration =  self._my_clip.duration
            duration = (duration/15 + 1 if duration%15 != 0 else duration/15)*15

            if che.QUOTA + duration > 57*60:
                err_msg = """ERROR - QUATA COULD EXCEED. Here is what u could do:
                    1. Try using a different account and manually reset the quota limit.
                    2. Wait until next month and try again."""
                raise Exception(err_msg)
            
            temp_folder_name = "temp_files"
            if keep_audio_file or keep_transcript_file:
                temp_folder_name = "additional_files"
            
            if not os.path.exists(temp_folder_name):
                os.mkdir(temp_folder_name)
            audio_file_path = os.path.join(temp_folder_name, self.video_file_name.split('.')[0] + "_audio.mp3")
            self._my_clip.audio.write_audiofile(audio_file_path)

            if os.stat(audio_file_path).st_size / (1024 * 1024) > 10:
                raise Exception("Cannot process audio files more than 10 mb.")
            
            print("Requesting API")
            results = self._api_request(audio_file_path=audio_file_path, service_account_json=service_account_json)
            che.update_cache(add_to_quota = duration)
            print("Received response. Processing response")
            transcript_data = self._process_transcript(results=results)
            print("Data processed")

            transcript_file_path=os.path.join(temp_folder_name, self.video_file_name.split('.')[0] + "_transcript.csv")
            transcript_data.to_csv(transcript_file_path, index=False)

            # print("Deleting temp files.")
            # self.delete_temp_file(
            #                 keep_audio_file=keep_audio_file,
            #                 keep_transcript_file=keep_transcript_file)
            
            
        else:
            # possible_temp_folders = ["/temp_files", "/Additional files"]
            # possible_file_names = ["transcript.csv", "transcript.xlsx"]
            # transcript_possible_paths = []
            # for folder in possible_temp_folders:
            #     for file in possible_file_names:
            #        transcript_possible_paths.append("/"+ folder + "/" + file)
            # # transcript_possible_paths = [lambda x: "/"+ y + "/" + x for y in possible_temp_folders for x in possible_file_names]
            # # transcript_possible_paths = ["/temp_files/transcript.csv", "/temp_files/transcript.excel", "/Additional files/transcript.csv", "/Additional files/transcript.excel"]
            # for pth in transcript_possible_paths:
            #     if os.path.exists(pth):
            #         transcript_file_path = pth
            #         break

            transcript_data = pd.read_csv(transcript_file_path)
            transcript_data = transcript_data.reset_index()
        
        print("populating db")
        populate_data(transcript_data=transcript_data)

        return transcript_data
        


        


        