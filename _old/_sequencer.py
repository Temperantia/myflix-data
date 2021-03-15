from json import dump, load

videos = load(open('data/videos.json', 'r', encoding='utf-8'))
shows = []
movies = []

for id in videos:
    video = videos[id]
    if video['summary']['type'] == 'show':
        shows.append(video)
    elif video['summary']['type'] == 'movie':
        movies.append(video)
dump({'results': shows}, open('data/shows.json', 'w', encoding='utf-8'),
     ensure_ascii=False, sort_keys=True, indent=2)
dump({'results': movies}, open('data/movies.json', 'w', encoding='utf-8'),
     ensure_ascii=False, sort_keys=True, indent=2)
