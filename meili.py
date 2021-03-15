import meilisearch

client = meilisearch.Client('https://search.my-flix.net')


def create_doc(video_id, video):
  doc = {
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
      'f': followers[id],
      'z': videos[id]['score'],  # scores[id]
      'q': rank[id],
      'p': popularity[id],
      'h': bingeworthiness[id],
      'newReleasesRank': new_releases[id] if id in new_releases else None,
      'monthRank': months[id] if id in months else None,
      'topSeriesRank': top_series[id] if id in top_series else None,
      'j': trending[video['t']] if video['t'] in trending else None,
  }
  if video['seasonCount']:
    doc['s'] = video['seasonCount']
  if video['episodeCount']:
    doc['e'] = video['episodeCount']
