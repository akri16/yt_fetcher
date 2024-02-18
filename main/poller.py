import datetime
import time
from typing import List
from .models import Video
from .config import youtube, mongo, settings
from dateutil.parser import isoparse
import logging


def get_time():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def get_timestamp_from_iso(iso_date: str):
    return isoparse(iso_date).timestamp()

def get_iso_from_timestamp(tstp: float):
    return datetime.datetime.fromtimestamp(tstp, datetime.timezone.utc).isoformat()

def store_videos(videos: list):
    if not videos:
        return
    
    for video in videos:
        video['pag_token'] = str(video['publishing_datetime']) + video['id']

    try:
        mongo.videos.insert_many(videos, ordered=False)
    except Exception as e:
        # logging.info(e)
        pass
    
def get_last_tstp_in_db():
    videos = list(mongo.videos.find({}).sort({'publishing_datetime': -1}).limit(1))
    if not videos:
        timestamp = 0
    else:
        timestamp = videos[0]['publishing_datetime']

    return get_iso_from_timestamp(timestamp)

def start_polling():
    last_video_tstp = get_last_tstp_in_db()
    logging.info(f"Starting Poller @ 1/{settings.poll_interval} hz")
    
    while True:
        request = youtube.search().list(
            part="snippet",
            maxResults=settings.poll_max_res,
            q=settings.poll_query,
            order="date",
            type="video",
            publishedAfter=last_video_tstp
        )

        response = request.execute()

        next_videos = []
        for item in response['items']:
            snippet = item['snippet']
            video = Video(
                id=item['id']['videoId'],
                title=snippet['title'],
                desp=snippet['description'],
                thumbnail=snippet['thumbnails']['default']['url'],
                publishing_datetime=get_timestamp_from_iso(snippet['publishTime'])
            )
            
            next_videos.append(video.model_dump())
        
        logging.info(f"API call at {get_time()} detected {len(next_videos)} videos")
        store_videos(next_videos)

        if next_videos:
            last_video_tstp = get_iso_from_timestamp(next_videos[0]['publishing_datetime'])

        time.sleep(settings.poll_interval)

   