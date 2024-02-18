import logging
import time
from typing import Any
from pydantic import Field, conlist
from pydantic_settings import BaseSettings
from pymongo import MongoClient
import googleapiclient.discovery
from googleapiclient.errors import HttpError


class Settings(BaseSettings):
    yt_api_keys: conlist(str, min_length=1) = [] # type: ignore
    mongo_conn_str: str = ""
    poll_interval: int = 10
    poll_query: str = "football"
    poll_max_res: int = 25


class YTAPIKeyManager:
    api_service_name = "youtube"
    api_version = "v3"
    all_token_exp_wt_time = 3600

    def __init__(self, api_keys: list[str]) -> None:
        services = []
        for key in api_keys:
            svc = googleapiclient.discovery.build(
                self.api_service_name, self.api_version, developerKey=key
            )
            services.append(svc)

        self.services = services
        self.curr_service_idx = 0
        self.N_services = len(services)

    def _next_token(self):
        self.curr_service_idx = (self.curr_service_idx + 1) % self.N_services

    def _svc(self) -> Any:
        return self.services[self.curr_service_idx]
    
    def run_request(self, requester):
        num_trial = 0
        while True:
            num_trial += 1
            
            try:
                return requester(self._svc()).execute()
            except HttpError as e:
                logging.info(e)
                self._next_token()

            if num_trial == self.N_services:
                logging.info(f'All Tokens Expired. Stalling Request for {self.all_token_exp_wt_time}s')
                time.sleep(self.all_token_exp_wt_time)
                num_trial = 0

settings = Settings()
mongo = MongoClient(settings.mongo_conn_str).yt_db
yt_manager = YTAPIKeyManager(settings.yt_api_keys)
logging.getLogger().setLevel(logging.INFO)
