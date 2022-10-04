import os
import pandas as pd
from typing import Any
import moviepy.editor as mp
import sqlite3

from config.config import LoadConfigs

cfg = LoadConfigs()

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
        self.transcript_db_path = cfg.TRANSCRIPT_DB_PATH

        self.con = sqlite3.connect( self.transcript_db_path)
    
    def _annotate(self, clip: Any, 
                txt: str): #Xolonium-Bold', fontsize=50
        """ Writes a text at the bottom of the clip. """        
        txtclip = mp.TextClip(txt, 
                                font=self.font, 
                                bg_color=self.bg_color, 
                                fontsize=self.fontsize, 
                                color=self.txt_color, 
                                align=self.align)
        cvc = mp.CompositeVideoClip([clip, txtclip.set_pos((self.x_pos, self.y_pos))]) #('center', 'bottom')
        return cvc.set_duration(clip.duration)

    def render_video(self):
        transcript_data = pd.read_sql("""SELECT * FROM transcript__data""", self.con)
        # print(transcript_data)
        annotated_clips = []
        for _, row in transcript_data.iterrows():
            annotated_clips.append(self._annotate(clip=self.my_clip.subclip(row['Start_Time'], row['End_Time']), 
                                                   txt=str(row['Content']))
                                    )
        
        final_clip = mp.concatenate_videoclips(annotated_clips)
        filename = os.path.join(cfg.TEMP_FILES_FOLDER, "edited_video_file.mp4")
        final_clip.write_videofile(filename=filename, fps = 24,
                                    codec=cfg.CODEC, 
                                    audio_codec=cfg.AUDIO_CODEC)

