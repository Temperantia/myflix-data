from logs import db as database, get_collection
from googleapiclient.discovery import build
from threads import threads
import time

liste = []

video_database = get_collection(database.collection('videos'), [])
for doc in video_database:
	video = doc.to_dict()
	liste.append([doc.id, video['title']])

api_key = "AIzaSyB_vrRbtutNWuB8g_ZpZAga2dwuidN2U4U" 

def get_trailer(id, title):
    videos = []
    youtube=build('youtube','v3',developerKey=api_key)
    next_page_token = None
    while 1:
        res = youtube.search().list(q=f'{title} Official Trailer', part='snippet',type='video', maxResults=50, pageToken=next_page_token).execute()
        videos += res['items']
        break 

    trailer = {'videoUrl' : 'https://www.youtube.com/watch?v='+(videos[0]['id']['videoId'])}
    database.collection('videos').document(id).update({'trailer': trailer})

threads(get_trailer, liste, 0.3)