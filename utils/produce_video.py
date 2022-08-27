import moviepy.editor as mp
from config.config import Load_Configs
from typing import Any
import sqlite3
import pandas as pd

cfg = Load_Configs()

class Produce_Video:
    def __init__(self, video_file_name: str):
        self.video_file_name = video_file_name
        self.my_clip = mp.VideoFileClip(video_file_name)
        clip_size = self.my_clip.size
        self.fontsize = int(clip_size[0]/24) * cfg.FONT_SIZE

        if cfg.X_POS == 'dynamic':
            self.x_pos = int(clip_size[0]/2)
        else:
            self.x_pos = cfg.X_POS

        if cfg.Y_POS == 'dynamic':
            self.y_pos = int((4*clip_size[1])/5)
        else:
            self.y_pos = cfg.Y_POS

        self.bg_color = cfg.BG_COLOR
        self.txt_color = cfg.FONT_COLOR
        self.font = cfg.FONT
        self.align = cfg.ALIGN
    
    def _annotate(self, clip: Any, 
                txt: str): #Xolonium-Bold', fontsize=50
        """ Writes a text at the bottom of the clip. """
        print(self.txt_color)
        
        txtclip = mp.TextClip(txt, 
                                font=self.font, 
                                bg_color=self.bg_color, 
                                fontsize=self.fontsize, 
                                color=self.txt_color, 
                                align=self.align)
        cvc = mp.CompositeVideoClip([clip, txtclip.set_pos((self.x_pos, self.y_pos))]) #('center', 'bottom')
        return cvc.set_duration(clip.duration)

    def render_video(self):
        con = sqlite3.connect("transcript.db")
        transcript_data = pd.read_sql("""SELECT * FROM transcript__data""", con)
        # print(transcript_data)
        annotated_clips = []
        for _, row in transcript_data.iterrows():
            print(type(row['start_time']), type(row['end_time']), type(row['content']))
            annotated_clips.append(self._annotate(clip=self.my_clip.subclip(row['start_time'], row['end_time']), 
                                                   txt=str(row['content']))
                                    )
        
        final_clip = mp.concatenate_videoclips(annotated_clips)
        # new = final_clip.set_audio(AudioFileClip("tmp_files/ML.mp3"))
        filename = self.video_file_name.split('.')[0] + cfg.OUTPUT_VIDEO_SUFFIX + ".mp4"
        final_clip.write_videofile(filename=filename, 
                                    codec=cfg.CODEC, 
                                    audio_codec=cfg.AUDIO_CODEC, 
                                    temp_audiofile=cfg.TEMP_AUDIO_FILE)

