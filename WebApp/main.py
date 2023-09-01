#!/usr/bin/python3
# -*- coding: utf-8 -*-

### General imports ###
from __future__ import division
import numpy as np
import pandas as pd
import time
import re
import os
from collections import Counter
import altair as alt

### Flask imports
import requests
from flask import Flask, render_template, session, request, redirect, flash, Response



### Video imports ###
from library.video_emotion_recognition import *

### Text imports ###
#from library.text_emotion_recognition import *
#from library.text_preprocessor import *
from nltk import *
from tika import parser
from werkzeug.utils import secure_filename
import tempfile



# Flask config
app = Flask(__name__)
app.secret_key = b'(\xee\x00\xd4\xce"\xcf\xe8@\r\xde\xfc\xbdJ\x08W'
app.config['UPLOAD_FOLDER'] = '/Upload'

################################################################################
################################## INDEX #######################################
################################################################################

# Home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

################################################################################
################################## RULES #######################################
################################################################################

# Rules of the game
@app.route('/rules')
def rules():
    return render_template('rules.html')

################################################################################
############################### VIDEO  ################################
################################################################################

# Read the overall dataframe before the user starts to add his own data
df = pd.read_csv('static/js/db/histo.txt', sep=",")

# Video interview template
@app.route('/video', methods=['POST'])
def video() :
    # Display a warning message
    flash('You will have 5 seconds to discuss the topic mentioned above. Due to restrictions, we are not able to redirect you once the video is over. Please move your URL to /video_dash instead of /video_1 once over. You will be able to see your results then.')
    return render_template('video.html')

# Display the video flow (face, landmarks, emotion)
@app.route('/video_1', methods=['POST'])
def video_1() :
    try :
        # Response is used to display a flow of information
        return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')
    #return Response(stream_template('video.html', gen()))
    except :
        return None

# Dashboard
@app.route('/video_dash', methods=("POST", "GET"))
def video_dash():
    
    # Load personal history
    df_2 = pd.read_csv('static/js/db/histo_perso.txt')


    def emo_prop(df_2) :
        return [int(100*len(df_2[df_2.density==0])/len(df_2)),
                    int(100*len(df_2[df_2.density==1])/len(df_2)),
                    int(100*len(df_2[df_2.density==2])/len(df_2)),
                    int(100*len(df_2[df_2.density==3])/len(df_2)),
                    int(100*len(df_2[df_2.density==4])/len(df_2)),
                    int(100*len(df_2[df_2.density==5])/len(df_2)),
                    int(100*len(df_2[df_2.density==6])/len(df_2))]

    emotions = ["Angry", "Disgust", "Fear",  "Happy", "Sad", "Surprise", "Neutral"]
    emo_perso = {}
    emo_glob = {}

    for i in range(len(emotions)) :
        emo_perso[emotions[i]] = len(df_2[df_2.density==i])
        emo_glob[emotions[i]] = len(df[df.density==i])

    df_perso = pd.DataFrame.from_dict(emo_perso, orient='index')
    df_perso = df_perso.reset_index()
    df_perso.columns = ['EMOTION', 'VALUE']
    df_perso.to_csv('static/js/db/hist_vid_perso.txt', sep=",", index=False)

    df_glob = pd.DataFrame.from_dict(emo_glob, orient='index')
    df_glob = df_glob.reset_index()
    df_glob.columns = ['EMOTION', 'VALUE']
    df_glob.to_csv('static/js/db/hist_vid_glob.txt', sep=",", index=False)

    emotion = df_2.density.mode()[0]
    emotion_other = df.density.mode()[0]

    def emotion_label(emotion) :
        if emotion == 0 :
            return "Angry"
        elif emotion == 1 :
            return "Disgust"
        elif emotion == 2 :
            return "Fear"
        elif emotion == 3 :
            return "Happy"
        elif emotion == 4 :
            return "Sad"
        elif emotion == 5 :
            return "Surprise"
        else :
            return "Neutral"

    ### Altair Plot
    df_altair = pd.read_csv('static/js/db/prob.csv', header=None, index_col=None).reset_index()
    df_altair.columns = ['Time', 'Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

    
    angry = alt.Chart(df_altair).mark_line(color='orange', strokeWidth=2).encode(
       x='Time:Q',
       y='Angry:Q',
       tooltip=["Angry"]
    )

    disgust = alt.Chart(df_altair).mark_line(color='red', strokeWidth=2).encode(
        x='Time:Q',
        y='Disgust:Q',
        tooltip=["Disgust"])


    fear = alt.Chart(df_altair).mark_line(color='green', strokeWidth=2).encode(
        x='Time:Q',
        y='Fear:Q',
        tooltip=["Fear"])


    happy = alt.Chart(df_altair).mark_line(color='blue', strokeWidth=2).encode(
        x='Time:Q',
        y='Happy:Q',
        tooltip=["Happy"])


    sad = alt.Chart(df_altair).mark_line(color='black', strokeWidth=2).encode(
        x='Time:Q',
        y='Sad:Q',
        tooltip=["Sad"])


    surprise = alt.Chart(df_altair).mark_line(color='pink', strokeWidth=2).encode(
        x='Time:Q',
        y='Surprise:Q',
        tooltip=["Surprise"])


    neutral = alt.Chart(df_altair).mark_line(color='brown', strokeWidth=2).encode(
        x='Time:Q',
        y='Neutral:Q',
        tooltip=["Neutral"])


    chart = (angry + disgust + fear + happy + sad + surprise + neutral).properties(
    width=1000, height=400, title='Probability of each emotion over time')

    chart.save('static/css/chart.html')
    
    return render_template('video_dash.html', emo=emotion_label(emotion), emo_other = emotion_label(emotion_other), prob = emo_prop(df_2), prob_other = emo_prop(df))

if __name__ == '__main__':
    app.run(debug=True)
