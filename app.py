import flask
from flask import Flask, redirect, url_for, render_template, flash, jsonify, abort, request
from flask_cors import cross_origin
import urllib.parse
import requests
# from YouPy import YouTubeItem
from pytube import YouTube
import os
import moviepy.editor as mp
import re
import pyrebase
from time import time
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from forms import RequestForm, EmailForm

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv()

from config import Config, Settings

app = Flask(__name__)
app.config.from_object(Config)

# FIREBASE
firebase = pyrebase.initialize_app(Settings.FIREBASE_CONFIG)
storage = firebase.storage()

with open(Settings.CRED_FILE, 'w') as outfile:
    json.dump(Settings.FIREBASE_CERT, outfile)

cred = credentials.Certificate(Settings.CRED_FILE)
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/', methods = ['GET', 'POST'])
def home():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        if checkEmailExist(email):
            return redirect(url_for('requestSong', email = email))
        abort(404)
    return render_template("index.html", form=form)


@app.route('/request:<email>', methods = ['GET', 'POST'])
def requestSong(email):
    form = RequestForm()
    if form.validate_on_submit():
        url = form.url.data
        title, mp3_path = convert(url)
        if not title and not mp3_path:
            msg = "URL Error: Please check URL entered."
            return render_template("msg.html", msg = msg, email = email)
        song_details = uploadMp3(email, title, mp3_path)        
        try:
            parsed_name = urllib.parse.quote_plus(song_details.get('name'))
        except:
            return redirect(url_for('message', msg = "Unable to get download URL.", email = email))
        download_url = "https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media&token={}".format(
            song_details['bucket'],
            parsed_name,
            song_details['downloadTokens'])
        os.remove(mp3_path)
        song = createFbSong(name = title, url = download_url)
        updateUserPlaylist(song, email)
        return redirect(url_for('playlist', email = email, msg = "Thank you for dedicating! Your song has been added to the playlist."))
    if checkEmailExist(email):
        return render_template("request.html", form = form, email = email)
    abort(404)


@app.route('/message?msg=<msg>&email=<email>', methods = ['GET'])
def message(msg, email = None):
    return render_template("msg.html", msg = msg, email = email)

@app.route('/playlist?email=<email>', methods = ['GET'])
@app.route('/playlist?email=<email>&msg=<msg>', methods = ['GET'])
def playlist(email, msg = None):
    doc_ref = db.collection(Settings.FB_COLLECTION).document(email)
    data = doc_ref.get().to_dict()
    if len(data['playlist']) <= 0:
        return render_template("msg.html", msg = "Playlist is empty", email = email)
    return render_template("playlist.html", email = email, msg = msg, data = data)


@app.route('/uploader:<email>', methods = ['POST'])
def upload_file(email):
    f = request.files['file']
    directory = os.path.join(Settings.BASE_DIR, Settings.MUSIC_DIR)
    if not os.path.exists(directory):
        os.makedirs(directory)
    mp3_path = os.path.join(Settings.BASE_DIR, Settings.MUSIC_DIR, secure_filename(f.filename))
    f.save(mp3_path)

    title = f.filename.replace('.mp3', '')

    song_details = uploadMp3(email, title, mp3_path)
    try:
        parsed_name = urllib.parse.quote_plus(song_details.get('name'))
    except:
        return redirect(url_for('message', msg = "Unable to get download URL.", email = email))
    download_url = "https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media&token={}".format(
        song_details['bucket'],
        parsed_name,
        song_details['downloadTokens'])
    os.remove(mp3_path)
    song = createFbSong(name = title, url = download_url)
    updateUserPlaylist(song, email)
    return redirect(url_for('playlist', email = email, msg = "Thank you for dedicating! Your song has been added to the playlist."))


@app.errorhandler(404)
def page_not_found(e):
    msg = "Error 404: Page could not be found"
    return render_template("msg.html", msg = msg, email = None)


def convert(url):
    print(url)
    folder = os.path.join(Settings.BASE_DIR, Settings.MUSIC_DIR)

    try:
        YouTube(url, request_headers = {'cookie': Settings.COOKIE}).streams.first().download(folder)
    except Exception as e:
        print(e)
        return None, None

    for filename in os.listdir(folder):
        if re.search('mp4', filename):
            mp4_path = os.path.join(folder,filename)
            title = os.path.splitext(filename)[0]+'.mp3'
            mp3_path = os.path.join(folder, title)
            new_file = mp.AudioFileClip(mp4_path)
            new_file.write_audiofile(mp3_path)
            os.remove(mp4_path)
            return os.path.splitext(filename)[0], mp3_path


def checkEmailExist(email):
    doc_ref = db.collection(Settings.FB_COLLECTION).document(email)
    doc = doc_ref.get()
    return doc.exists


def uploadMp3(email, title, mp3_path):
    path_on_cloud = "{}/{}".format(email, title)
    return storage.child(path_on_cloud).put(mp3_path)


def updateUserPlaylist(song, email):
    doc_ref = db.collection(Settings.FB_COLLECTION).document(email)
    doc = doc_ref.get()
    if doc.exists:
        playlist = doc.to_dict().get(Settings.FB_PLAYLIST_FIELD)
        playlist.append(song)
        doc_ref.update({
            Settings.FB_PLAYLIST_FIELD: playlist,
            Settings.FB_TIMESTAMP_FIELD: int(time()*1000)
        })
    else:
        print(u'No such document!')


def createFbSong(url, name = "Unknown", cover = "https://github.com/u3u.png", artist = "Unknown"):
    return {
        "name": name,
        "cover": cover,
        "artist": artist,
        "url": url
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)