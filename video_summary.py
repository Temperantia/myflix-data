
from requests import post

from utils import threads, file
from key import netflix
from video_ids import get_ids


def fetch_video(id: str, shows_with_summary):
  data = {
      "path": """["videos", """ + id + """, "summary"]"""}
  try:
    response = post(netflix.url, json=data, headers=netflix.headers).json()
    objects = response['jsonGraph']['videos']
    for video_id in objects:
      video = objects[video_id]
      summary = video['summary']['value'] if 'summary' in video and 'value' in video['summary'] else None
      if summary and 'type' in summary and not summary['type'] == 'episode' and not summary['type'] == 'supplemental':# and ('$type' in summary or summary['$type'] == 'error'):
        shows_with_summary[video_id] = {
            'summary': summary,
        }
  except:
    print('error ' + id)

# Summaries are the only way known to identify proper titles, ids need to be individually fetched


def get_summary():
  shows_with_summary = file.read_json('data/video_summary.json')
  args = [[id, shows_with_summary] for id in get_ids()]
  threads(fetch_video, args, 0.02, 'Fetching summaries')
  print('Collected ' + str(len(shows_with_summary)) + ' shows and movies')
  file.write_json('data/video_summary.json', shows_with_summary)
  return shows_with_summary
