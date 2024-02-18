import datetime
from dateutil.parser import isoparse


def get_time():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def get_timestamp_from_iso(iso_date: str):
    return isoparse(iso_date).timestamp()

def get_iso_from_timestamp(tstp: float):
    return datetime.datetime.fromtimestamp(tstp, datetime.timezone.utc).isoformat()