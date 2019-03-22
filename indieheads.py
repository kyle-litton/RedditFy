#!/usr/bin/env python
import requests
import csv
import time
import spotipy
import spotipy.util as util
from bs4 import BeautifulSoup


url = "https://old.reddit.com/r/indieheads/top/"
# Headers to mimic a browser visit
headers = {'User-Agent': 'Mozilla/5.0'}

# Returns a requests.models.Response object
page = requests.get(url, headers=headers)

soup = BeautifulSoup(page.text, 'html.parser')

albumLinks = []
trackLinks = []

for data in soup.find_all('p', class_='title'):
    for a in data.find_all('a'):
        if 'spotify.com/album' in a.get('href'):
            albumLinks.append(a.get('href'))


        if 'spotify.com/track' in a.get('href'):
            trackLinks.append(a.get('href'))




scope = 'playlist-modify-public'
username = '99kylel'


token = util.prompt_for_user_token(username,scope,client_id='',client_secret='',redirect_uri='http://localhost/')


if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
   
    for x in albumLinks:

        temp = []
        temp = sp.album_tracks(x)

        #temporary fix, issue when non-released album posted
        try:
            test = temp['tracks']
        except KeyError:
            continue
       
        for s in temp['tracks']['items']:

             trackLinks.append(s['id'])

    existing_tracks = sp.user_playlist_tracks(token,'75svY6VFRSQ1CCXZa6t9Bk')

    uriList = []

    #prevents adding duplicate songs
    dupCheck = []
    for x in existing_tracks['items']:
        dupCheck.append(x['track']['id'])


    for c in trackLinks:

        t = sp.track(c).get('uri')[14:]
        if t not in dupCheck:
            uriList.append(t)




    if uriList: 
        results = sp.user_playlist_add_tracks(username, '75svY6VFRSQ1CCXZa6t9Bk', uriList)
        print("New songs have been added to r/indieheads")
    else:
        print("Nothing new to add to playlist")


else:
    print("Can't get token for", username)
