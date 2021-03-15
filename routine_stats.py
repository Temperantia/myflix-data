from statistics import mean
from datetime import datetime, timedelta
from calendar import monthrange
from typing import Any, Dict, List, Tuple
from random import uniform
import meilisearch

from utils import firebase, threads

scores: Dict[str, float] = {}
followers: Dict[str, int] = {}
videos: Dict[str, Any] = {}
rank: Dict[str, int] = {}
popularity: Dict[str, int] = {}
bingeworthiness: Dict[str, float] = {}
categories: Dict[str, Dict[str, Any]] = {}
new_releases: Dict[str, int] = {}
months: Dict[str, int] = {}
top_series: Dict[str, int] = {}

client = meilisearch.Client('https://search.my-flix.net')
dt = datetime.now()
start = (dt - timedelta(days=dt.weekday())).replace(hour=0,
                                                    minute=0, second=0, microsecond=0)
end = (start + timedelta(days=7)).timestamp()
start_release = (start - timedelta(days=7)).timestamp()
start = start.timestamp()

_, month_day_end = monthrange(dt.year, dt.month)
month_start = (dt.replace(day=1, minute=0,
                          second=0, microsecond=0)).timestamp()
month_end = (dt.replace(day=month_day_end, minute=0,
                        second=0, microsecond=0)).timestamp()

trending: Dict[str, int] = {
    "The Queen's Gambit": 3
}


def get_video_stat(video_id: str, video: Dict[str, Any]):
  global followers, scores, bingeworthiness
  # hardcoded
  video['score'] = round(video['Rating'] - uniform(0.1, 0.4),
                         1) if 'Rating' in video and video['Rating'] else None
  followers[video_id] = int(video['IMDbFollowers'] * 1000 /
                            2358519) if 'IMDbFollowers' in video and video['IMDbFollowers'] else 0

  # followers[video_id] = len(
  #    video['followers']) if 'followers' in video and video['followers'] else 0
  # video['score'] = mean(list(video['scores'].values())
  #                      ) if 'scores' in video and video['scores'] else None
  scores[video_id] = video['score'] if 'score' in video and video['score'] else 0
  bingeworthiness[video_id] = len(video['bingeworthiness']) / \
      2 if 'bingeworthiness' in video and video['bingeworthiness'] else 0
  for category in video['categories']:
    if category in categories:
      categories[category]['value'] += 1
    else:
      categories[category] = {'category': category,
                              'value': 1, 'image': video['boxArt']}


def upload(video_id: str, video):
  global rank, popularity
  video.update({
      'rank': rank[video_id],
      'popularity': popularity[video_id],
  })
  firebase.video_collection.document(video_id).set(video, merge=True)


def get_video_stats(videos: Dict[str, Any]):
  global rank, popularity
  print('Stats')
  ordered: List[Tuple[str, float]] = sorted(
      scores.items(), key=lambda elem: elem[1], reverse=True)
  for index, (id, _) in enumerate(ordered):
    rank[id] = index + 1

  new_release_index = 1
  month_index = 1
  top_series_index = 1
  show_count = 0
  film_count = 0

  ordered = sorted(followers.items(), key=lambda elem: elem[1], reverse=True)
  for index, (id, _) in enumerate(ordered):
    video = videos[id]
    availability = video['availability']['availabilityStartTime'] / \
        1000 if 'availability' in video and video['availability']['availabilityStartTime'] else None
    popularity[id] = index + 1
    if availability and availability >= start_release and availability <= end:
      new_releases[id] = new_release_index
      new_release_index += 1
    if availability and availability >= month_start and availability <= month_end:
      months[id] = month_index
      month_index += 1
    if video['summary']['type'] == 'show':
      top_series[id] = top_series_index
      top_series_index += 1
      show_count += 1
    else:
      film_count += 1

  firebase.globals_collection.document('globals').update({
      'newReleaseCount': new_release_index,
      'filmCount': film_count,
      'showCount': show_count
  })

  print('Most popular categories')
  client.index('categories').delete_all_documents()
  client.index('categories').add_documents(sorted(categories.values(),
                                                  key=lambda elem: elem['value'], reverse=True)[:3])
  # to thread

  print('Upload')
  threads.threads(upload, [[video_id, video]
                           for video_id, video in videos.items()], 0, 'Uploading')

  print('Updating search tables')
  search = [{
      'id': video_id,
      'r': video['route'],
      't': video['title'],
      'i': video['Poster'] if 'Poster' in video else video['boxArt'],
      'b': video['storyArt'],
      'c': video['categories'],
      'g': video['genres'],
      'y': video['releaseYear'],
      'v': video['maturity'],
      'd': video['synopsis'],
      'a': video['availability']['availabilityStartTime'],
      'u': 1 if video['summary']['type'] == 'show' else 0,
      'z': video['score'],
      'imdbLongName': video['LongIMDbTitle'] if 'LongIMDbTitle' in video else '',
      'o': 1 if video['summary']['isOriginal'] else 0,
      'f': followers[video_id],
      'z': video['score'],
      'q': rank[video_id],
      'p': popularity[video_id],
      'h': bingeworthiness[video_id],
      'newReleasesRank': new_releases[video_id] if video_id in new_releases else None,
      'monthRank': months[video_id] if video_id in months else None,
      'topSeriesRank': top_series[video_id] if video_id in top_series else None,
      'j': trending[video['title']] if video['title'] in trending else None,
      's': video['seasonCount'] if video['seasonCount'] else None,
      'e': video['episodeCount'] if video['episodeCount'] else None,
  } for video_id, video in videos.items()]

  client.index('videos').update_documents(search)
