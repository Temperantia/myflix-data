from typing import Any, Dict, List
from slugify import slugify
from random import uniform, randint
import meilisearch
from datetime import datetime


from utils import file, firebase, threads

"""
a : availability
b : story art
c : category
d : description / synopsis
e : episode number
f : follower number
g : genres
h : bingeworthy
i : image / tall box art
j : trending
m : current month
n : current new release (< 2 weeks)
o : original
p : popularity
q : rank
r : route
s : season count
t : title
u : type 1 = show 0 = movie
v : video maturity
w : current week
y : release year
z : score

"""

types = {}
title_ids: Dict[int, int] = {}
search: List[Dict[str, Any]] = []

f: Dict[str, Any] = file.read_json('data/videos.json').items()
items = {id: video for id, video in f if 'title' in video and video['title']}
items = sorted(items.items(), key=lambda item: (not item[1]['title'][0].isalpha(
), item[1]['title']))
data = {k: v for k, v in items}

f: Dict[str, Dict[str, str]] = file.read_json('data/genres_tagged.json')
genre_dict: Dict[str, List[str]] = {}
for category in f:
  for genre_id in f[category]:
    genre = f[category][genre_id]
    if not genre in category:
      genre_dict[genre] = []
    genre_dict[genre].append(category)

client = meilisearch.Client('https://search.my-flix.net')
show_count = 0
film_count = 0


def create_route(title: str, type: str, id: int) -> str:
  global types, title_ids
  start = datetime.now()

  route = ('/tvshows/' if type == 'show' else '/films/') + \
      slugify(title + ('-' + str(id) if id > 0 else '')) + '/overview'
  if route in types and types[route] == type:
    if not id in title_ids:
      title_ids[id] = 1
    else:
      title_ids[id] += 1
    route = create_route(title, type, title_ids[id])
  types[route] = type
  print('route took ', str(datetime.now() - start))
  return route


def find_categories(genres: Dict[str, str]):
  categories: List[str] = []
  for genre in genres:
    categories += genre_dict[genre]
  return categories


def search_videos(video: Dict[str, Any], id: str):
  global search
  doc = {
      'id': id,
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
      'o': 1 if video['summary']['isOriginal'] else 0
  }

  if video['seasonCount']:
    doc['s'] = video['seasonCount']
  if video['episodeCount']:
    doc['e'] = video['episodeCount']
  search.append(doc)


def upload(id: str, data: Dict[str, Any]):
  global show_count, film_count
  video = data[id]

  if video['summary']['type'] == 'show':
    show_count += 1
  else:
    film_count += 1

  video.update({
      'route': create_route(video['title'], video['summary']['type'], 0),
      'categories': find_categories(video['genres']),
  })

  # if not 'exists' in video:

  rating: float=round(video['Rating'] - uniform(0.1, 0.4),
                        1) if 'Rating' in video and video['Rating'] else None
  video: Dict[str, Any]={
      **video,
      'scores':  {str(index): rating for index in range(
          randint(200, 700))} if rating else {},
      'score': rating,
      'favorites': [],
      'exists': True
  }

  #firebase.video_collection.document(id).set(video, merge=True)
  search_videos(video, id)


if __name__ == '__main__':
  args=[[id, data] for id in data]
  # args = [args[0]]
  threads.threads(upload, args, 0, 'Uploading titles')

  client.index('videos').update_documents(search)

  file.write_json('data/videos.json', data)
  firebase.globals_collection.document('globals').update(
      {'showCount': show_count, 'filmCount': film_count})
