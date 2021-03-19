from typing import Any, Dict
from random import randint
from datetime import datetime

import query_netflix
import media
import imdbpy
import scrape_imdb
import routine_stats

from utils import firebase, threads, file

QUERY_NETFLIX = True  # 40 minutes
QUERY_NETFLIX_MEDIA_CENTER = False  # 10 minutes # TODO BUG
QUERY_IMDB = True
QUERY_YOUTUBE = True
SCRAPE_IMDB = True  # ?
CALCULATE_STATS = True
SEED_FIRESTORE = False

dt = datetime.now()


def get_video(video_id: str, video: Dict[str, Any]):
  if QUERY_NETFLIX_MEDIA_CENTER:
    media.request_media(video_id, video)
  if QUERY_IMDB:
    imdbpy.get_imdb_data(video)
  if QUERY_YOUTUBE:
    pass
  if SCRAPE_IMDB and 'IMDbID' in video:
    scrape_imdb.main_page(video)
  if CALCULATE_STATS:
    routine_stats.get_video_stat(video_id, video)


videos: Dict[str, Any] = {}

if QUERY_NETFLIX:
  query_netflix.get_videos(videos)
  print('Queried Netflix')

#videos.update(file.read_json('data/videos.json'))
args = [[video_id, video] for video_id, video in videos.items()]
threads.threads(get_video, args, 0, 'Getting videos')
file.write_json('data/videos.json', videos)

if SEED_FIRESTORE:
  for video_id, video in videos.items():
    if video['exists']:
      continue
    follower_number = int(video['IMDbFollowers'] * 1000 /
                          2358519) if 'IMDbFollowers' in video and video['IMDbFollowers'] else 0
    firebase.video_collection.document(video_id).update({
        'scores':  {str(index): video['score'] for index in range(
            randint(200, 700))} if video['score'] else {},
        'followers':  {str(index): dt for index in range(follower_number)},
        'favorites': [],
        'exists': True
    })

if CALCULATE_STATS:
  routine_stats.get_video_stats(videos)
