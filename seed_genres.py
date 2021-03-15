
from requests import post
from key import netflix
from utils import threads, file

genres = {}


def rangeCollect(index: int):
  ids = [i for i in range(index, index + 8000)]
  data = {
      "path": """["genres", """ + str(ids) + """, "name"]"""}
  try:
    response = post(netflix.url, json=data, headers=netflix.headers).json()
  except:
    print('Error from ' + str(index))
  print('Collected range ' + str(index))
  objects = response['jsonGraph']['genres']
  for genreId in objects:
    genre = objects[genreId]
    if 'value' in genre['name'] and genre['name']['value'] is not None:
      genres[genreId] = genre['name']['value']


args = [[ids * 8000] for ids in range(12500)]
threads.threads(rangeCollect, args, 0.5, 'Collecting genres')
file.write_json('data/genres.json', genres)
