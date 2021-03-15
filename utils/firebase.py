from typing import Any, Dict, List
from firebase_admin import credentials, firestore, initialize_app

production: bool = True

cred: credentials.Certificate = credentials.Certificate(
    'key/my-flix-91e46-firebase-adminsdk-tx9sq-c48bb4e2a9.json')
if production:
  cred: credentials.Certificate = credentials.Certificate(
      'key/myflix-prod-firebase-adminsdk-un9jx-59d53b5c76.json')

initialize_app(cred)
db = firestore.client()
video_collection = db.collection('videos')
data_collection = db.collection('data')
genre_collection = db.collection('genres')
stats_collection = db.collection('stats')
globals_collection = db.collection('globals')
users_collection = db.collection('users')
reviews_collection = db.collection('reviews')


limit = 1000  # Reduce this if it uses too much of your RAM


def get_collection(collection, cursor=None):
  data: Dict[str, Any] = {}
  while True:
    query = collection.limit(limit)
    if cursor:
      query = query.start_after(cursor)
    docs: List[Any] = [snapshot for snapshot in query.stream()]
    data.update({snapshot.id: snapshot.to_dict() for snapshot in docs})
    if len(docs) == limit:
      print('1000 docs fetched')

      cursor = docs[limit-1]
      continue
    print('Finished fetching')
    return data.items()
