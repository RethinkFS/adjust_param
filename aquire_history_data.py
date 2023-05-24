from enum import unique, Enum

import pandas as pd

DATA_PATH="./history_data.csv"
START_ADJUST_THRESHOLD=10

# continuous_param
CONTINUOUS_PARAM={
    "gc_start_level",
    "gc_slope",
    "gc_sleep_time",
    "finish_threshold_",
}

# discrete_param
DISCRETE_PARAM={
    "ZBD_ABSTRACT_TYPE",
    "RAID_LEVEL",
}

# continuous_param range
CONTINUOUS_PARAM_RANGE= {
    "gc_start_level": {"min": 0, "max": 0},
    "gc_slope": {"min": 0, "max": 0},
    "gc_sleep_time": {"min": 0, "max": 0},
    "finish_threshold_": {"min": 0, "max": 0},
}

@unique
class ZBD_ABSTRACT_TYPE(Enum):
    ZONEFS=1
    ZBD=2
ZBD_ABSTRACT_TYPE_LIST = [ZBD_TYPE for ZBD_TYPE in ZBD_ABSTRACT_TYPE]

@unique
class RAID_LEVEL(Enum):
    RAID0=1
    RAID1=2
    RAID5=3
RAID_LIST=[RAID for RAID in RAID_LEVEL]
# print(RAID_LIST)

# discrete_param range
DISCRETE_PARAM_RANGE={
    "ZBD_ABSTRACT_TYPE": ZBD_ABSTRACT_TYPE_LIST,
    "RAID_LEVEL": RAID_LIST,
}


# 将收集到的历史数据以series的列表返回
def history_data():
    history_dataframe = pd.read_csv(DATA_PATH)
    # if len(history_dataframe) < START_ADJUST_THRESHOLD:
    #     return False, []
    data_list = []
    for _, data in history_dataframe.iterrows():
        data_list.append(data)
    return True, data_list

# history_data()
