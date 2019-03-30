from setup import parse_args
from types import SimpleNamespace
import csv
import time
import spotipy
import spotipy.util as util
import configparser
import praw
import json

#setup
args = parse_args()

#Configuration load
config=configparser.ConfigParser()
config.read('mylogin.ini')

#TODO Add an array for subreddits or a command line args
url = ["indieheads"]
keywords = ["FRESH ALBUM","FRESH"]

#Set the permissions
scope = 'playlist-modify-public'
username = config['LOGIN']['username']

#LOAD PRAW
reddit = praw.Reddit(config['REDDIT']['username'],user_agent='redditpy')

#Load the spotify client using the contents of 'mylogin.ini'
token = util.prompt_for_user_token(username,scope=scope,client_id=config['LOGIN']['clientID'],client_secret=config['LOGIN']['clientSecret'],redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    albumTitles = []
    trackTitles = []
    trackLinks = []

    #Loop through all the subs that were defined
    for sub in url:
        musicSub = reddit.subreddit(sub).top(limit=args.limit,time_filter=args.filter)
        for post in musicSub:

            #spotify album link
            #Check if the post title contains any of the keywords
            if any(x in post.title for x in keywords):
                #
                if "https://open.spotify.com/album/" in post.url:
                    album = sp.album_tracks(post.url)

                    try:
                        #Two different dic types that it returns
                        test = album['tracks']['items']
                        for song in album['tracks']['items']:
                            trackLinks.append(song['id'])
                    
                    except KeyError:
                        for song in album['items']:
                            trackLinks.append(song['id'])                   

                #If there is a spotify track
                elif "spotify.com/track" in post.url:
                    trackLinks.append(post.url)
                    print(post.url)

                #Song without spotify link
                else:
                    print(post.url)
                    url = post.url

                    search = sp.search(url[7:], limit = 1, offset = 0, type = 'track', market = None)
                    if search['tracks']['total'] > 0:
                        for s in search['tracks']['items']:
                            if(len(trackLinks)<100):
                                trackLinks.append(s['id']) 
    
    uriList = []
    dontRemove = []

    #prevents adding duplicate songs
    existing_tracks = sp.user_playlist_tracks(token,config['SPOTIFY']['redditPlaylist'])
    dupCheck = []
    for x in existing_tracks['items']:
        dupCheck.append(x['track']['id'])


    for c in trackLinks:

        t = sp.track(c).get('uri')[14:]
        if t not in dupCheck:
            uriList.append(t)
        else:
            dontRemove.append(t)

    existing_tracks = sp.user_playlist_tracks(token,config['SPOTIFY']['redditPlaylist'])

    #keeps playlist to a max 100 songs
    if((existing_tracks['total']+len(uriList))>100):
        dTracks = []
        count = (existing_tracks['total']+len(trackLinks))-100
        
        for x in existing_tracks['items']:

            if (count is not 0) and (x['track']['id'] not in dontRemove):
                dTracks.append(x['track']['id'])
                count = count - 1
       
        sp.user_playlist_remove_all_occurrences_of_tracks(username, config['SPOTIFY']['redditPlaylist'], dTracks, snapshot_id=None)

    
    #Add the songs
    if uriList: 
        results = sp.user_playlist_add_tracks(username, config['SPOTIFY']['redditPlaylist'], uriList)
        print("New songs have been added to reddit playlist")
    else:
        print("Nothing new to add to playlist")
        
else:
    print("Can't get token for", username)
    
