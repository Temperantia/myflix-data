from typing import Any, Dict, List
from requests import post
from json import dumps

from utils import threads, file
from key import netflix


def rangeCollect(index: int, rng: int, videos: Dict[str, Any]):
  ids = [str(i) for i in range(index, index + rng)]
  data = {
      "path": """["videos", """ + dumps(ids) + """, "title"]"""}
  try:
    response = post(netflix.url, json=data, headers=netflix.headers, timeout=10)
    print(response)
    response = response.json()
    objects = response['jsonGraph']['videos']
    for video_id in objects:
      video = objects[video_id]
      if 'value' in video['title'] and isinstance(video['title']['value'], str):
        value = video['title']['value'].strip()
        if value:
          videos[video_id] = {'title': value}
  except Exception as e:
    return
    print(e)
    print('error ' + str(index))


# Ensures the ids are their own parent meaning they are proper titles or episodes
def get_titles(index: List[int], videos: Dict[str, Any], videos_cleaned: Dict[str, Any]):
  data = {
      "path": '["videos", ' + dumps(index) + ', "parent"]'}
  try:
    response = post(netflix.url, json=data, headers=netflix.headers, timeout=10).json()
    print(response)
    objects = response['jsonGraph']['videos']
    for (video_id, video) in objects.items():
      if 'value' in video['parent'] and isinstance(video['parent']['value'], list) and len(video['parent']['value']) == 2 and video['parent']['value'][1] == video_id:
        videos_cleaned[video_id] = videos[video_id]
  except Exception as e:
    return
    print(e)
    print(index[0])


def get_ids():
  videos = file.read_json('data/video_ids.json')
  args: List[List[Any]] = []
  # 60 000 000 to 82 000 000
  for i in range(5):  # range(5):  # 60_037_677
    index = 60_000_000 + i * 8000
    args.append([index, 8000, videos])
  for i in range(39):  # 70_309_703
    index = 70_000_000 + i * 8000
    args.append([index, 8000, videos])
  for i in range(496):  # 80 240 263
    index = 80_000_000 + i * 500
    args.append([index, 500, videos])
  for i in range(3040):  # 80_986_788 - 81 290 762 = 303,974
    index = 80_986_788 + i * 100
    args.append([index, 100, videos])
  threads.threads(rangeCollect, args, 0.1, 'Scanning ids')
  print('Collected ' + str(len(videos)) + ' ids')

  video_cleaned = file.read_json('data/video_cleaned.json')
  count = 0
  id_list: List[List[Any]] = []
  for id in videos:
    if count % 150 == 0:
      if count != 0:
        id_list[-1] = [id_list[-1], videos, video_cleaned]
      id_list.append([])
    id_list[-1].append(id)
    count += 1

  if len(id_list) > 1:
    id_list[-1] = [id_list[-1], videos, video_cleaned]
  threads.threads(get_titles, id_list, 0.1, 'Purging ids')
  print('Collected ' + str(len(video_cleaned)) + ' titles and trailers')
  file.write_json('data/video_cleaned.json', video_cleaned)
  return video_cleaned

get_ids()