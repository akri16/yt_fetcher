import logging
from pydantic_settings import BaseSettings
from pymongo import MongoClient
import googleapiclient.discovery


class Settings(BaseSettings):
    yt_api_key: str = ""
    mongo_conn_str: str = ""
    poll_interval: int = 10
    poll_query: str = "football"
    poll_max_res: int = 25


settings = Settings()
mongo = MongoClient(settings.mongo_conn_str).yt_db
api_service_name = "youtube"
api_version = "v3"
api_key = settings.yt_api_key

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=api_key)

logging.getLogger().setLevel(logging.INFO)