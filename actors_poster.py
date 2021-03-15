import imdb
from firebase import db as database, get_collection
from threads import threads

video_database = database.collection('videos').limit(3).stream() #get_collection(database.collection('videos'), [])

ids = []

for doc in video_database:
	video = doc.to_dict()
	ids.append([doc.id, video])

db = imdb.IMDb(accessSystem='https', reraiseExceptions=True)

def update_actors(id, video):

	try:
		if 'Actors' in video:
			save = {}
			actor_dict = video['Actors']
			for actor in actor_dict:
				role = actor_dict[actor]
				search = db.search_person(str(actor))
				if len(search)>0:
					actor = search[0]
					name = actor["name"]
					save[name] = {
						'poster': actor['full-size headshot'] if 'full-size headshot' in actor.keys() else None,
						'role': role
					}
			database.collection('videos').document(id).update({'Actors': save})
	except:
		print('e')
	
threads(update_actors, ids, 0.3)