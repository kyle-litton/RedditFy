#!/usr/bin/env python
import requests
import csv
import time
import spotipy
import spotipy.util as util
from bs4 import BeautifulSoup


url = "https://old.reddit.com/r/hiphopheads/top/"
# Headers to mimic a browser visit
headers = {'User-Agent': 'Mozilla/5.0'}

# Returns a requests.models.Response object
page = requests.get(url, headers=headers)

soup = BeautifulSoup(page.text, 'html.parser')

scope = 'playlist-modify-public'
username = '99kylel'


token = util.prompt_for_user_token(username,scope,client_id='',client_secret='',redirect_uri='http://localhost/')


if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
        

    albumTitles = []
    trackTitles = []

    trackLinks = []

    for data in soup.find_all('p', class_='title'):
        for a in data.find_all('a'):
            
            #spotify album link
            if 'spotify.com/album' in a.get('href') and ('[FRESH ALBUM]' in a.text or'[FRESH]' in a.text):
                temp = []
                temp = sp.album_tracks(a.get('href'))
                print(a.text)
                #fix odd error where delux albums are different structs
                try:
                    test = temp['tracks']
                except KeyError:
                    for s in temp['items']:
                    
                        if(len(trackLinks)<100):
                            trackLinks.append(s['id'])
                    continue
           
                for s in temp['tracks']['items']:
                    
                    if(len(trackLinks)<100):
                        trackLinks.append(s['id'])
                       

            #spotify track link
            elif 'spotify.com/track' in a.get('href') and '[FRESH]' in a.text:
                trackLinks.append(a.get('href'))
                print(a.text)

            #Album without spotify link
            elif '[FRESH ALBUM]' in a.text:
                x = a.text
                search = sp.search(x[13:], limit = 1, offset = 0, type = 'album', market = None)
                print(a.text)
                if search['albums']['total'] > 0:
                    for s in search['albums']['items']:
                        temp = []
                        temp = sp.album_tracks(s['id'])

                        #temporary fix, issue when non-released album posted
                        try:
                            test = temp['tracks']
                        except KeyError:
                            continue
           
                        for b in temp['tracks']['items']:
                          
                            if(len(trackLinks)<100):
                                trackLinks.append(b['id']) 
                               
                
            #Song without spotify link
            elif '[FRESH]' in a.text:
                print(a.text)
                x = a.text
                
                search = sp.search(x[7:], limit = 1, offset = 0, type = 'track', market = None)
            
                if search['tracks']['total'] > 0:

                    for s in search['tracks']['items']:
                        if(len(trackLinks)<100):
                            trackLinks.append(s['id'])

    uriList = []
    dontRemove = []

    #prevents adding duplicate songs
    existing_tracks = sp.user_playlist_tracks(token,'6L13eWId1qkQibMJLKAcI5')
    dupCheck = []
    for x in existing_tracks['items']:
        dupCheck.append(x['track']['id'])


    for c in trackLinks:

        t = sp.track(c).get('uri')[14:]
        if t not in dupCheck:
            uriList.append(t)
        else:
            dontRemove.append(t)


          
    existing_tracks = sp.user_playlist_tracks(token,'6L13eWId1qkQibMJLKAcI5')

    #keeps playlist to a max 100 songs
    if((existing_tracks['total']+len(uriList))>100):
        dTracks = []
        count = (existing_tracks['total']+len(trackLinks))-100
        
        for x in existing_tracks['items']:

            if (count is not 0) and (x['track']['id'] not in dontRemove):
                dTracks.append(x['track']['id'])
                count = count - 1
       
        sp.user_playlist_remove_all_occurrences_of_tracks(username, '6L13eWId1qkQibMJLKAcI5', dTracks, snapshot_id=None)

    


    if uriList: 
        results = sp.user_playlist_add_tracks(username, '6L13eWId1qkQibMJLKAcI5', uriList)
        print("New songs have been added to r/hiphopheads")
    else:
        print("Nothing new to add to playlist")


else:
    print("Can't get token for", username)
