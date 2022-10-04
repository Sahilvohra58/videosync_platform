import pandas as pd
import os

def populate_data(transcript_dataframe: pd.DataFrame, Transcript_Data_Class, db):
    transcript_db_path = './transcript.db'
    if os.path.exists(transcript_db_path):
        os.remove(transcript_db_path)
    db.create_all()
    for _, row in transcript_dataframe.iterrows():
        append_data = Transcript_Data_Class(
            Content = row["Content"],
            Start_Time = float(row["Start_Time"]),
            End_Time = float(row['End_Time']),
        )
        db.session.add(append_data)
        db.session.commit()