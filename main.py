import argparse
import logging
from flask import redirect, send_file
from config.config import Load_Configs
from utils.caching import Cache
from utils.speech_to_text import Speech_To_Text
from utils.produce_video import Produce_Video
from app import app

parser = argparse.ArgumentParser(description='Importing video file name and other optional requirements')

# Required positional argument
parser.add_argument('--video_file_name', type=str,
                    help='The video file name to be processed. Must be a .mp4 file')

parser.add_argument('--service_account_json', #type=str,
                    help='The credentials file for GCP connection')

# Optional positional argument
parser.add_argument('--transcript_file_path', type=str,
                    help='Path if you already have a transcript.')

# Optional positional argument
parser.add_argument('--app_port', type=str,
                    help='Port to run the app')

# Optional positional argument
parser.add_argument('--keep_transcript_file', action='store_true',
                    help='To get the csv file of transcript')

parser.add_argument('--keep_audio_file', action='store_true',
                    help='To retain the audio file')

parser.add_argument('--verbose', default=0, action='store_const', const=1,
                    help='To print logs: 0, 1')


args = parser.parse_args()

video_file_name = args.video_file_name
transcript_file_path = args.transcript_file_path
service_account_json=args.service_account_json,
keep_audio_file=args.keep_audio_file,
keep_transcript_file=args.keep_transcript_file
app_port = args.app_port

if args.verbose == 1:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

if video_file_name[-4:] != ".mp4":
    raise ValueError("Only .mp4 files can be processed!!!")

cfg = Load_Configs()
che = Cache()
s2t = Speech_To_Text()


@app.route('/produce', methods=['GET', 'POST'])
def produce():
    # render_template('<b>producing video</b>')
    Produce_Video(video_file_name=video_file_name).render_video()
    s2t.delete_temp_file(keep_audio_file=keep_audio_file,
                        keep_transcript_file=keep_transcript_file)
    return redirect('/download')

@app.route('/download')
def download_file():
    path = video_file_name.split('.')[0] + '_edited.mp4'
    return send_file(path, as_attachment=True)

def main():

    s2t.generate_subtitles( 
        video_file_name=args.video_file_name,
        service_account_json=args.service_account_json,
        transcript_file_path=args.transcript_file_path,
        keep_audio_file=args.keep_audio_file,
        keep_transcript_file=args.keep_transcript_file)

    
    app.run(port=app_port ,debug=True)


if __name__ == "__main__":
    main()

#/Users/savohra/opt/anaconda3/envs/ai-video-editor/bin/python /Users/savohra/Desktop/ai-subtitle-video-editor/main.py --video_file_name Sahil.mp4 --service_account_json service-account.json --transcript_file_path 'Sahil_transcript.csv'