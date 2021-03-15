from json import load
from firebase import genre_collection

data = load(open('data/genres_tagged.json', 'r', encoding='utf-8'))
for category in data:
  print('Uploading ' + category)
  genre_collection.document(category).set(data[category])
