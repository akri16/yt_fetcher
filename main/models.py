from pydantic import BaseModel


class Video(BaseModel):
    id: str
    title: str
    desp: str
    publishing_datetime: float
    thumbnail: str

class PaginatedVideos(BaseModel):
    max_page: int
    curr_page: int
    page_size: int
    videos: list[Video]