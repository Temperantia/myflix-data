from json import load, dump

genres = load(open('data/genres.json', 'r', encoding='utf-8'))
tags = {'action': ['action'],
        'anime': ['anime', 'manga'],
        'asian': ['japan', 'indian', 'korean', 'chinese', 'thai', 'indonesian', 'pakistani', 'malaysian', 'hindi', 'bollywood', 'taiwanese', 'filipino', 'hong kong', 'singaporean', 'punjabi', 'bengali', 'tamil'],
        'british': ['british'],
        'comedies': ['comedies', 'comédies'],
        'crime': ['crime'],
        'docuseries': ['docuseries', 'documentaries'],
        'dramas': ['dramas'],
        'foodTravel': ['food', 'travel'],
        'history': ['historical']
        }
found = {}
for genre in genres:
    name = genres[genre].lower()
    for tag in tags:
        if tag not in found:
            found[tag] = []
        keywords = tags[tag]
        for keyword in keywords:
            if keyword in name and genre not in found[tag]:
                print(genre + ' : ' + name)
                found[tag].append(genre)
dump(found, open('data/genre-ids.json', 'w', encoding='utf-8'),
     ensure_ascii=False, sort_keys=True, indent=2)
