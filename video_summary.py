
from typing import Any, Dict
from requests import post

from utils import threads, file
from key import netflix
from video_ids import get_ids


def fetch_video(id: str, shows_with_summary: Dict[str, Any]):
  data = {
      "path": """["videos", """ + id + """, "summary"]"""}
  try:
    response = post(netflix.url, json=data, headers=netflix.headers)
    print(data)
    print(response)
    response = response.json()
    objects = response['jsonGraph']['videos']
    for video_id in objects:
      video = objects[video_id]
      print(video)
      summary = video['summary']['value'] if 'summary' in video and 'value' in video['summary'] else None
      # and ('$type' in summary or summary['$type'] == 'error'):
      if summary and 'type' in summary and not summary['type'] == 'episode' and not summary['type'] == 'supplemental':
        shows_with_summary[video_id] = {
            'summary': summary,
        }
  except:
    print(id)
    return
    print('error ' + id)

# Summaries are the only way known to identify proper titles, ids need to be individually fetched


def get_summary() -> Dict[str, Any]:
  shows_with_summary = file.read_json('data/video_summary.json')
  args = [[id, shows_with_summary] for id in get_ids()]
  threads.threads(fetch_video, args, 0.1, 'Fetching summaries')
  print('Collected ' + str(len(shows_with_summary)) + ' shows and movies')
  file.write_json('data/video_summary.json', shows_with_summary)
  return shows_with_summary
