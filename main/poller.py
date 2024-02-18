import time
from typing import List
from main.api import videos

from main.utils import get_iso_from_timestamp, get_time, get_timestamp_from_iso
from .models import Video
from .config import yt_manager, mongo, settings
import logging


def build_search_requester(last_time):
    def requester(service):
        return service.search().list(
            part="snippet",
            maxResults=settings.poll_max_res,
            q=settings.poll_query,
            order="date",
            type="video",
            publishedAfter=last_time
        )
    return requester

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

def extract_videos(response):
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
    return next_videos
    
def get_last_tstp_in_db():
    videos = list(mongo.videos.find({}).sort({'publishing_datetime': -1}).limit(1))
    if not videos:
        timestamp = 0
    else:
        timestamp = videos[0]['publishing_datetime']

    return get_iso_from_timestamp(timestamp)

def start_polling():
    logging.info(f"Starting Poller @ 1/{settings.poll_interval} hz")
    
    last_video_tstp = get_last_tstp_in_db()
    while True:
        requester = build_search_requester(last_video_tstp)
        response = yt_manager.run_request(requester)

        videos = extract_videos(response)
        store_videos(videos)
        
        logging.info(f"API call at {get_time()} detected {len(videos)} videos")
        
        if videos:
            last_video_tstp = get_iso_from_timestamp(videos[0]['publishing_datetime'])

        time.sleep(settings.poll_interval)

   