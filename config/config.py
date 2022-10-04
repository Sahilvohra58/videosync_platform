import yaml
import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


class LoadConfigs:
    def __init__(self):
        with open(os.path.join(ROOT_PATH, "config.yaml"), 'r') as stream:
            cfg = yaml.safe_load(stream)
            self.UPLOAD_DIRECTORY = cfg['UPLOAD_DIRECTORY']
            self.ALLOWED_VIDEO_EXTENSIONS = cfg['ALLOWED_VIDEO_EXTENSIONS']
            self.ALLOWED_JSON_EXTENSIONS = cfg['ALLOWED_JSON_EXTENSIONS']
            self.ALLOWED_TRANSCRIPT_EXTENSIONS = cfg['ALLOWED_TRANSCRIPT_EXTENSIONS']
            self.DB_DIRECTORY = cfg['DB_DIRECTORY']
            self.TEMP_FILES_FOLDER = cfg['TEMP_FILES_FOLDER']
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
            self.CODEC = cfg['CODEC']
            self.AUDIO_CODEC = cfg['AUDIO_CODEC']
            self.TRANSCRIPT_DB_PATH = cfg['TRANSCRIPT_DB_PATH']


# if __name__ == "__main__":
#     cfg = LoadConfigs()
#     print(vars(cfg))