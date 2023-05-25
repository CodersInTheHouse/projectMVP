import spotipy.util as util
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-read-recently-played"
clientID='55d23f0684a24570bb4e3cb9b59cacbf'
clientSe ='77429b32ade848e19cce3769cc7e10bd'
redirect='http://localhost:7777/callback'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=clientID,client_secret=clientSe,redirect_uri=redirect,scope=scope))

results = sp.current_user_recently_played(limit=10)
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])

scope = "user-top-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=clientID,client_secret=clientSe,redirect_uri=redirect,scope=scope))

results = sp.current_user_top_artists(limit=10)
for idx, artist in enumerate(results['items']):
    print(idx, artist['name'],artist['popularity'],artist['genres'],artist['images'][0])

results = sp.current_user_top_tracks()
for idx, item in enumerate(results['items']):
    artists=[artist['name'] for artist in item['artists']]
    print(idx, item['name'],artists)
    

