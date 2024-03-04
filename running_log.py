import time
import datetime

date_format = '%Y-%m-%d %H:%M:%S'


def running_log(log: str, Rm=None):
    date = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)
    v = Rm.selected_version if Rm is not None else ""
    print(f"[{date}]: {v} {log}")
