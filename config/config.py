import yaml
import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


class Load_Configs:
    def __init__(self):
        with open(os.path.join(ROOT_PATH, "config.yaml"), 'r') as stream:
            cfg = yaml.safe_load(stream)
            self.SERVICE_ACCOUNT_FILE_NAME = cfg['SERVICE_ACCOUNT_FILE_NAME']
            self.SAMPLE_RATE_HERTZ = cfg['SAMPLE_RATE_HERTZ']
            self.ENABLE_AUTOMATIC_PUNCTUATION = cfg['ENABLE_AUTOMATIC_PUNCTUATION']
            self.ENABLE_WORD_TIME_OFFSETS = cfg['ENABLE_WORD_TIME_OFFSETS']
            self.LANGUAGE_CODE = cfg['LANGUAGE_CODE']
            self.BG_COLOR = cfg['BG_COLOR']
            self.FONT_COLOR = cfg['FONT_COLOR']
            self.FONT = cfg['FONT']
            self.FONT_SIZE = cfg['FONT_SIZE']
            self.X_POS = cfg['X_POS']
            self.Y_POS = cfg['Y_POS']
            self.ALIGN = cfg['ALIGN']
            self.OUTPUT_VIDEO_SUFFIX = cfg['OUTPUT_VIDEO_SUFFIX']
            self.CODEC = cfg['CODEC']
            self.AUDIO_CODEC = cfg['AUDIO_CODEC']
            self.TEMP_AUDIO_FILE = cfg['TEMP_AUDIO_FILE']
