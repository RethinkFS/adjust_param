import json
import os
import pandas as pd
import numpy as np
import requests
import time
from var_blk_size import create_null_blk, remove_null_blk, SECT_SIZE, ZONE_SIZE
from aquire_history_data import history_data, CONTINUOUS_PARAM
from adjust_param import adjust

SECT_SIZE_PARAM = 512
ZONE_SIZE_PARAM = 32
BENCH_NAME = "../build/db_bench"
ACQUIRE_CONFIG = "../build/plugin/aquafs/defconfig"
CREATE_TMP_FILE = "mkdir -p /tmp/aquafs ;\
sudo ../build/plugin/aquafs/aquafs mkfs --zbd nullb0 --aux-path /tmp/aquafs"
class Prometheus():
    def __init__(self, ip):
        self.server_ip = ip
        self.pre_url = self.server_ip + "/api/v1/query?query="
        self.pre_url_range = self.server_ip + "/api/v1/query_range?query="

    def get_range_write_throughput(self, start_time, end_time, step):
        expr = "aquafs_write_throughput&start=%s&end=%s&step=%s" % (start_time, end_time, step)
        url = self.pre_url_range + expr
        print("collecting all write throughput results: visiting \n"+url)
        # collect data through prometheus
        res = json.loads(requests.post(url=url).content.decode('utf8', 'ignore'))
        target = []
        # for throughput in res.get("data").get("result")[3]:
        #     target.append(throughput.get("values"))
        # print(res.get("data").get("result"))
        # print(res.get("data").get("result")[3])
        for throughput in res.get("data").get("result")[3].get("values"):
            target.append(int(throughput[1]))
        return target

PROMETHEUS_IP = "http://localhost:9090"
prometheus = Prometheus(PROMETHEUS_IP)

def collect_range_param_and_throughput(sect_size,zone_size,start_time,end_time,step):
    # collect history data
    throughput_list = prometheus.get_range_write_throughput(start_time, end_time, step)
    avg_throughput = int(np.average(throughput_list))
    # collect corresponding params
    is_adjust, datas = history_data()
    # new_data_num = len(throughput_list)
    # prepare target list
    throughput_list = [data[-1] for data in datas] + [avg_throughput]
    # prepare param
    history_param = [data[:-1] for data in datas]
    print(os.popen(ACQUIRE_CONFIG).readlines())
    param_dict = json.loads(os.popen(ACQUIRE_CONFIG).readlines()[0])
    param_series = pd.Series(param_dict)

    # default param
    param_series["sect_size"]=sect_size
    param_series["zone_size"]=zone_size
    param_series["finish_threshold_"] = 0
    param_series["ZBD_ABSTRACT_TYPE"] = 1
    param_series["RAID_LEVEL"] = 1

    param_list = history_param + [param_series]
    param_throughput = []
    print("param list : {}".format(param_list))
    # print("len of param_list : {}".format(len(param_list)))
    # print("len of throughput : {}".format(len(throughput_list)))
    print("throughput list : {}".format(throughput_list))
    for s, v in zip(param_list, throughput_list):
        s["TARGET"] = v
        param_throughput.append(s)
    # add new params and throughput to history_data.csv
    record_data = pd.DataFrame(param_throughput)
    record_data.to_csv("history_data.csv", index=False)
    # return params and throughput
    print("param_throughput : {}".format(param_throughput))
    return param_throughput, avg_throughput

def execute_adjust_param(n, sect_size, zone_size):
    global SECT_SIZE_PARAM
    global ZONE_SIZE_PARAM
    # db_bench not exists in current directory
    if os.path.exists(BENCH_NAME) == False:
        print("Do not exist db_bench")
        return False, []
    # loop n times, get recommend params and then run the next params
    param = " --fs_uri=aquafs://dev:nullb0" \
            " --benchmarks=fillrandom --use_direct_io_for_flush_and_compaction --use_stderr_info_logger" 
    throughput_list = []
    for i in range(n):
        # collect throughput and corresponding parameters
        print("The {}-th adjust".format(i))
        execute_file_name = BENCH_NAME + param
        start_time = time.time()
        os.system(execute_file_name)
        end_time = time.time()
        step = (end_time - start_time) / 4
        param_throughput, avg_throughput = collect_range_param_and_throughput(sect_size,zone_size,start_time, end_time, step)
        throughput_list.append(avg_throughput)
        recommend = adjust(param_throughput, 2)
        SECT_SIZE_PARAM = recommend["sect_size"]
        ZONE_SIZE_PARAM = recommend["zone_size"]
        print("recommend params : {}".format(recommend))
        param = " --fs_uri=aquafs://dev:nullb0 " \
                "--benchmarks=fillrandom --use_direct_io_for_flush_and_compaction --use_stderr_info_logger"
        # for i in range(len(recommend)):
        #     param = param + " " + list(recommend.index)[i] + "=" + str(recommend[i])+" "
    return throughput_list

# for sect_size in SECT_SIZE:
#     for zone_size in ZONE_SIZE:
#         create_null_blk(sect_size, zone_size, 0, 64)
#         os.system(CREATE_TMP_FILE)
#         execute_adjust_param(1, sect_size, zone_size)
#         remove_null_blk()


pre_throughput = 0
now_throughput = 0
for _ in range(1):
    sect_size = SECT_SIZE_PARAM
    zone_size = ZONE_SIZE_PARAM
    total_throughput = []
    for i in range(2):
        create_null_blk(sect_size, zone_size, 0, 64)
        os.system(CREATE_TMP_FILE)
        throughput_list = execute_adjust_param(2, sect_size, zone_size)
        total_throughput = total_throughput + throughput_list
        print("throughput list : {}".format(total_throughput))
        remove_null_blk()
    print("sect_size:{}".format(sect_size))
    print("zone_size:{}".format(zone_size))
    pre_throughput = now_throughput
    now_throughput = np.average(total_throughput)

print("Throughput from {} to {}, increase {}".format(pre_throughput, now_throughput, (now_throughput-pre_throughput)/pre_throughput))

# execute_adjust_param(2)
# s1 = pd.Series([1,2,3], index=['a','b','c'])
# s2 = pd.Series([11,22,33], index=['a','b','c'])
# s3 = pd.Series([111,222,333], index=['a','b','c'])
# df = pd.DataFrame([s1, s2])
# print(df)
# df.to_csv('test', index=False)
# execute_adjust_param(2)
# a = [1,2,3]
# b = [3,4,5]
# for k, v in zip(a, b):
#     print(k, v)
# l = [s1,s2,s3]
# index = [1,2]
# test = []
# for k, v in zip(l,index):
#     k["d"]=v
#     print(k)
#     test.append(k)
# print(test)