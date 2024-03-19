import time
import datetime

date_format = '%Y-%m-%d %H:%M:%S'


def running_log(log: str):
    date = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)
    print(f"[{date}]: {log}")
