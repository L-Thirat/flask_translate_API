from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS, cross_origin

import requests
import speech_recognition as sr
import base64
from scipy.io import wavfile
import numpy as np
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

ffmpeg = "<dir>/ffmpeg-N-99395-ga3a6b56200-win64-gpl-shared/bin/ffmpeg.exe"


def convert_mkv2mp4(webm, wav):
    command = "%s -i %s -acodec pcm_s16le -ac 1 -ar 16000 ./%s" % (ffmpeg, webm, wav)
    print(subprocess.call(command, shell=True))


def convert_mp42wav(filename):
    command = "%s -i output.mp4 -acodec pcm_s16le -ac 1 -ar 16000 output.wav" % ffmpeg
    print(subprocess.call(command, shell=True))


@app.route("/app/", methods=["POST"])
def index():
    if request.method == "POST":
        print("FORM DATA RECEIVED")

        # load voice data
        data = request.get_data()
        data = str(data).split(",")[-1][:-1]

        # datetime object containing current date and time
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d%m%Y_%H%M%S")
        filename = "record/" + dt_string

        # convert video files
        webm_filname = filename + ".webm"
        wav_filename = filename + ".wav"
        wav_file = open(webm_filname, "wb")
        decode_string = base64.b64decode(data)
        wav_file.write(decode_string)
        convert_mkv2mp4(webm_filname, wav_filename)
        file = open(wav_filename, 'r')

        # voice recognition
        transcript = ""
        if file:
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(wav_filename)
            with audioFile as source:
                data = recognizer.record(source)
            try:
                transcript = recognizer.recognize_google(data, key=None)
            except:
                print("Translate Filed")
        return jsonify({"data": transcript})


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
