import re
import time
import datetime

date_format = '%Y-%m-%d %H:%M:%S'


def running_log(log: str):
    date = datetime.datetime.fromtimestamp(time.time()).strftime(date_format)
    print(f"[{date}]: {log}")


def remove_origin_lore(seq: str):
    while seq.endswith("原文{/lore}{/size}"):
        lore_start = seq.rfind("{size=*0.5}{lore=")
        seq = seq[:lore_start]
    return seq


def remove_flag(input_: str):
    # 为原文lore准备
    input_ = remove_origin_lore(input_)

    input_ = input_.replace('{i}', '').replace('{/i}', '')
    input_ = input_.replace('{b}', '').replace('{/b}', '')
    input_ = input_.replace('{s}', '').replace('{/s}', '')
    input_ = input_.replace('[', '').replace(']', '')

    input_ = input_ = re.sub(r'{size=[-+]?\d+}', '', input_).replace('{/size}', '')
    input_ = input_ = re.sub(r'{lore=.*?}', '', input_).replace('{/lore}', '')
    input_ = input_.replace('{rb}', '').replace('{/rb}', '')
    input_ = input_ = re.sub(r'{rt}.*?{/rt}', '', input_).replace('{/lore}', '')

    return input_
