import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = True

class Settings(object):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MUSIC_DIR = "music"
    GDRIVE_FOLDER = "Song_dedi_playlist"
    FIREBASE_CONFIG = {
        "apiKey": os.getenv('apiKey'),
        "authDomain": os.getenv('authDomain'),
        "databaseURL": os.getenv('databaseURL'),
        "projectId": os.getenv('projectId'),
        "storageBucket": os.getenv('storageBucket'),
        "messagingSenderId": os.getenv('messagingSenderId'),
        "appId": os.getenv('appId'),
        "measurementId": os.getenv('measurementId')
    }
    FIREBASE_CERT = {
        "type": os.getenv('type'),
        "project_id": os.getenv('projectId'),
        "private_key_id": os.getenv('private_key_id'),
        "private_key": os.getenv('private_key').replace("\\n", "\n"),
        "client_email": os.getenv('client_email'),
        "client_id": os.getenv('client_id'),
        "auth_uri": os.getenv('auth_uri'),
        "token_uri": os.getenv('token_uri'),
        "auth_provider_x509_cert_url": os.getenv('auth_provider_x509_cert_url'),
        "client_x509_cert_url": os.getenv('client_x509_cert_url')
    }
    CRED_FILE = "cred.json"
    FB_COLLECTION = "playlists"
    FB_PLAYLIST_FIELD = "playlist"
    FB_TIMESTAMP_FIELD = "timestamp"
    PROJECT_ID = "playlist-1596698015099"