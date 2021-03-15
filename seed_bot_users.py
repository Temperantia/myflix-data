from utils import firebase, threads
names = open('constant/john.txt', 'r').read().split('\n')


def create_bot_user(index: int):
  name = names[index]
  firebase.users_collection.document(str(index)).set({
      'bot': True,
      'email': None,
      'username': name,
      'usernameLower': name,
      'image': None,
      'reviews': [],
      'suggestions': [],
      'flixlist': {},
      'favorites': {'films': {}, 'shows': {}},
      'created': firebase.firestore.SERVER_TIMESTAMP,
      'providers': {}
  })


threads.threads(create_bot_user, [[index]
                                  for index in range(1000)], 0, 'Creating bots')
