import os
from pathlib import Path
from typing import List
from datetime import datetime, timedelta

def get_json_files() -> List[str]:
    files = []
    for file in os.listdir(Path.cwd() / "config"):
        if (file.endswith('.json')):
            files.append(file.split('.')[0])
    return files

def nearest_future(future, interval=120):
    """
    Get the neatest future time.
    Return the last one if two things will finish within `interval`.
    If the time is in the past, return current time + interval.

    Args:
        future (datetime.datetime or list[datetime.datetime]):
        interval (int): Seconds

    Returns:
        datetime.datetime:
    """
    # Convert single datetime to list
    if not isinstance(future, list):
        future = [future]

    future = [datetime.fromisoformat(f) if isinstance(
        f, str) else f for f in future]
    future = sorted(future)
    next_run = future[0]

    # 检查时间是否已经过去，如果是则返回当前时间+interval
    now = datetime.now()
    if next_run <= now:
        return now + timedelta(seconds=interval)

    for finish in future:
        if finish - next_run < timedelta(seconds=interval):
            next_run = finish

    return next_run


def dict_to_kv(dictionary, allow_none=True):
    """
    Args:
        dictionary: Such as `{'path': 'Scheduler.ServerUpdate', 'value': True}`
        allow_none (bool):

    Returns:
        str: Such as `path='Scheduler.ServerUpdate', value=True`
    """
    return ', '.join([f'{k}={repr(v)}' for k, v in dictionary.items() if allow_none or v is not None])
