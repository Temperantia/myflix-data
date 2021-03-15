import imdb

db = imdb.IMDb(accessSystem='https', reraiseExceptions=True)


def get_imdb_data(video):
  obj = {}

  try:
    movies = db.search_movie(video['title'])
    if len(movies) > 0:
      movie = movies[0]
      db.update(movie)
      keys = movie.keys()
      obj = {
          'OriginalTitle': movie['original title'] if 'original title' in keys else None,
          'LongIMDbTitle': movie['long imdb title'] if 'long imdb title' in keys else None,
          'IMDbID': movie['imdbID'] if 'imdbID' in keys else None,
          'Poster': movie['full-size cover url'] if 'full-size cover url' in keys else None,
          'Rating': movie['rating'] if 'rating' in keys else None,
          'Countries': movie['countries'] if 'countries' in keys else None,
          'Languages': movie['languages'] if 'languages' in keys else None,
      }

      if 'production companies' in keys:
        obj['ProductionCompanies'] = []
        for company in movie['production companies']:
          if not company['name'] in obj['ProductionCompanies']:
            obj['ProductionCompanies'].append(company['name'])

      if 'distributors' in keys:
        obj['DistributorCompanies'] = []
        for company in movie['distributors']:
          if not company['name'] in obj['DistributorCompanies']:
            obj['DistributorCompanies'].append(company['name'])

      if 'special effects' in keys:
        obj['SpecialEffects'] = []
        for company in movie['special effects']:
          if not company['name'] in obj['SpecialEffects']:
            obj['SpecialEffects'].append(company['name'])

      if 'other companies' in keys:
        obj['OtherCompanies'] = []
        for company in movie['other companies']:
          if not company['name'] in obj['OtherCompanies']:
            obj['OtherCompanies'].append(company['name'])

      if 'plot outline' in keys:
        obj['PlotOutline'] = movie['plot outline']

      if 'plot' in keys:
        temp = str(movie['plot']).split('::')
        obj['Plot'] = temp[0].replace("['", "")

      if 'cast' in keys:
        obj['Actors'] = {}
        for actor in movie['cast']:
          role = actor.currentRole
          obj['Actors'][actor['name']] = role['name'] if 'name' in role else None

  except Exception as e:
    print(e)
  video.update(obj)
