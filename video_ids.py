from typing import Any, List, Tuple
from requests import post
from json import dumps

from utils import threads, file
from key import netflix

error = 0


def rangeCollect(index: int, rng: int, videos):
  global error
  ids = [str(i) for i in range(index, index + rng)]
  data = {
      "path": """["videos", """ + dumps(ids) + """, "title"]"""}
  try:
    response = post(netflix.url, json=data, headers=netflix.headers)
    print(response)

    response = response.json()
    objects = response['jsonGraph']['videos']
    for video_id in objects:
      video = objects[video_id]
      if '$type' in video['title'] and video['title']['$type'] == 'error':
        error += 1
      elif 'value' in video['title'] and isinstance(video['title']['value'], str):
        value = video['title']['value'].strip()
        if value:
          videos[video_id] = {'title': value}
  except Exception as e:
    print(e)
    print('error ' + str(index))


# Ensures the ids are their own parent meaning they are proper titles or episodes
def get_titles(index, videos_cleaned, videos):
  data = {
      "path": '["videos", ' + dumps(index) + ', "parent"]'}
  try:
    response = post(key.url, json=data, headers=key.headers).json()
    objects = response['jsonGraph']['videos']
    for (video_id, video) in objects.items():
      if 'value' in video['parent'] and isinstance(video['parent']['value'], list) and len(video['parent']['value']) == 2 and video['parent']['value'][1] == video_id:
        videos_cleaned[video_id] = videos[video_id]
  except Exception as e:
    print(e)
    print(index[0])


def get_ids():
  videos = {}.fromkeys(['28369403',
                        '28630857',
                        '28631029',
                        '28631995',
                        '28634944'], {}).update(file.read_json('data/video_ids.json'))
  args: List[Tuple[int, int, Any]] = []
  # 60 000 000 to 82 000 000
  for i in range(5):  # 60_037_677
    index = 60_000_000 + i * 8000
    args.append((index, 8000, videos))
  for i in range(39):  # 70_309_703
    index = 70_000_000 + i * 8000
    args.append((index, 8000, videos))
  for i in range(496):  # 80 240 263
    index = 80_000_000 + i * 500
    args.append((index, 500, videos))
  for i in range(3040):  # 80_986_788 - 81 290 762 = 303,974
    index = 80_986_788 + i * 100
    args.append((index, 100, videos))
  args = [args[0]]
  threads.threads(rangeCollect, args, 0.02, 'Scanning ids')
  print(error)
  print('Collected ' + str(len(videos)) + ' ids')
  # with open('data/video_ids.json', 'w', encoding='utf-8') as outfile:
  #  dump(videos, outfile, ensure_ascii=False)

  videos_cleaned = file.read_json('data/video_cleaned.json')
  count = 0
  id_list = []
  for id in videos:
    if count % 150 == 0:
      if count != 0:
        id_list[-1] = [id_list[-1], videos_cleaned, videos]
      id_list.append([])
    id_list[-1].append(id)
    count += 1
  id_list[-1] = [id_list[-1], videos_cleaned, videos]
  threads.threads(get_titles, id_list, 0.02, 'Purging ids')
  print('Collected ' + str(len(videos_cleaned)) + ' titles and trailers')
  file.write_json('data/video_cleaned.json', videos_cleaned)
  return videos_cleaned

if __name__ == '__main__':
  get_ids()
