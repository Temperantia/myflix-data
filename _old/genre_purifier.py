from json import load, dump

tags = load(open('data/tags.json', 'r', encoding='utf-8'))
genres = load(open('data/genres.json', 'r', encoding='utf-8'))

words = ['starring', 'directed by', 'created by',
         'critically-acclaimed', 'award-winning', 'emmy-winning', 'oscar-winning', 'irreverent', 'visually-striking', 'visually striking', 'chilling', 'emotional', 'sentimental', 'gritty', 'exciting', 'inspiring', 'imaginative', 'violent', 'gory']


found = {'Other': {}}
for tag in tags:
    found[tag] = {}
cut = {}
for genre in genres:
    name = genres[genre].lower()

    exists = False
    for tag in tags:
        keywords = tags[tag]
        if any(keyword == name or keyword + ' ' in name or ' ' + keyword in name or keyword + '-' in name or '-' + keyword in name for keyword in keywords):
            found[tag][genre] = genres[genre]
            exists = True
    if exists:
        continue
    if any(word == name or word + ' ' in name or ' ' + word in name for word in words):
        continue
    found['Other'][genre] = genres[genre]

dump(found, open('data/genres_tagged.json', 'w', encoding='utf-8'),
     ensure_ascii=False, sort_keys=True, indent=2)

dump(cut, open('data/genres_cut.json', 'w', encoding='utf-8'),
     ensure_ascii=False, sort_keys=True, indent=2)
