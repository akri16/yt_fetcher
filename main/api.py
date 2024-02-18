from math import ceil
from fastapi import FastAPI, HTTPException, Query
from .config import mongo
from main.models import PaginatedVideos, Video


app = FastAPI(title="YT Video Fetcher", version="1.0.0")

@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}

@app.get("/videos", response_model=PaginatedVideos)
async def videos(
    query: str, 
    page_size: int = Query(10, gt=0, le=20), 
    page_no: int = 1,
    ascending: bool = False
) -> PaginatedVideos:

    # pag_token is a specially created field (publishTime + videoID). This field 
    # helps in paginatio as publishTime alone will not be unique

    data = mongo.videos.aggregate(
        [
            {
                '$match' : { '$text': { '$search': query } }
            },
            {
                '$sort': {
                    'pag_token': 1 if ascending else -1
                }
            },
            {
                '$facet': {
                    'metadata': [{ '$count': 'count' }],
                    'data': [{ '$skip': (page_no - 1) * page_size }, { '$limit': page_size }]
                }   
            }
        ]
    ).next()

    videos = data['data']
    if metadata := data['metadata']:
        cnt = metadata[0]['count']
    else:
        cnt = 0

    return PaginatedVideos(
        max_page=ceil(cnt/page_size),
        curr_page=page_no,
        page_size=len(videos),
        videos=videos
    )

