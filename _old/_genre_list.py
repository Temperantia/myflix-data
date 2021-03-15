
from requests import post
from json import dump, load, dumps
from time import sleep
from threading import Thread
from netflix import url, headers

genres = {}
videos = load(open('data/videos.json', 'r', encoding='utf-8'))

genre_ids = {}
for id in videos:
    video = videos[id]
    for genre in video['genres']:
        genre_ids[genre] = True

def genre_seek(ids):
    data = {
        "path": """["genres", """ + dumps(ids) + """, "name"]"""}
    response = post(url, json=data, headers=headers).json()
    objects = response['jsonGraph']['genres']
    for genreId in objects:
        genre = objects[genreId]
        if 'value' in genre['name'] and genre['name']['value'] is not None:
            genres[genreId] = genre['name']['value']


count = 0
id_list = []
for id in genre_ids:
    if count % 8000 == 0:
        id_list.append([])
    id_list[-1].append(int(id))
    count += 1

threads = []
for ids in id_list:
    threads.append(Thread(target=genre_seek, args=(ids,)))
for t in threads:
    t.start()
    sleep(0.02)
for t in threads:
    t.join()
dump(genres, open('data/genres.json', 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True, indent=2)
