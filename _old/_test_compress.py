import zlib
import json
from firebase import data_collection

f = json.dumps(json.load(open('data/videos.json', encoding='utf-8'))['70290905'])
print(len(f))
js = zlib.compress(f.encode('utf-8'))
print(str(js))
print(zlib.decompress(js))

doc = data_collection.document('search0').get().to_dict()['search']
print(list(doc))
print(type(doc))
print(zlib.decompress(doc))
