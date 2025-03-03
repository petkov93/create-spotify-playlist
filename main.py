import os

import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
# replace Spotify client id / secret with yours id/ secret
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_secret = os.getenv('SPOTIFY_SECRET')
scope = "user-library-read playlist-modify-public"
spotify_search_api = 'https://api.spotify.com/v1/search'

year = input('which year?: ')

date = f'{year}-12-31'

billboard = f'https://www.billboard.com/charts/hot-100/{date}/'
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}

with requests.get(billboard, headers=header) as response:
    soup = BeautifulSoup(response.text, 'html.parser')
top100songs = [song.get_text().strip() for song in soup.select('li ul li h3')]
# top100artists = [artist.get_text().strip() for artist in soup.select('li ul li h3 + span')]
# top100final = [f'{artist} - {song}' for (artist, song) in zip(top100artists, top100songs)]
# # print(top100final)
# print(top100songs)

# write the songs to a file
with open('text.txt', mode='w') as file:
    for line in top100songs:
        file.writelines(line + '\n')

# authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    client_id=spotify_client_id,
    client_secret=spotify_secret,
    redirect_uri='http://example.com',
    cache_path='.cache'))

user_id = sp.current_user()['id']

new_playlist = sp.user_playlist_create(
    user=user_id,
    name=f'Top 100 songs of {year}',
    public=True,
    collaborative=False,
    description='My first playlist done with Python')
song_uris = []
for song in top100songs:
    sp_song = sp.search(q=f'track:{song} year:{year}', type='track', limit=1)
    try:
        song_uri = sp_song['tracks']['items'][0]['uri']
        song_uris.append(song_uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

sp.playlist_add_items(playlist_id=new_playlist['id'], items=song_uris)

print('playlist created!')
