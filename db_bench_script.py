import json
import os
import pandas as pd
import requests
import time
from aquire_history_data import history_data, CONTINUOUS_PARAM
from adjust_param import adjust

BENCH_NAME = "../build/db_bench"
ACQUIRE_CONFIG = "../build/plugin/aquafs/defconfig"
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
        print(res.get("data").get("result"))
        print(res.get("data").get("result")[3])
        for throughput in res.get("data").get("result")[3].get("values"):
            target.append(throughput[1])
        return target

PROMETHEUS_IP = "http://localhost:9090"
prometheus = Prometheus(PROMETHEUS_IP)

def collect_range_param_and_throughput(start_time, end_time, step):
    # collect history data
    throughput_list = prometheus.get_range_write_throughput(start_time, end_time, step)
    print("data from prometheus : \n {}".format(throughput_list))
    # collect corresponding params
    is_adjust, datas = history_data()
    # prepare target list
    throughput_list = [data[-1] for data in datas] + throughput_list
    # prepare param
    history_param = [data[:-1] for data in datas]
    print(os.popen(ACQUIRE_CONFIG).readlines())
    param_dict = json.loads(os.popen(ACQUIRE_CONFIG).readlines()[0])
    param_series = pd.Series(param_dict)

    # default param
    param_series["finish_threshold_"] = 0
    param_series["ZBD_ABSTRACT_TYPE"] = 1
    param_series["RAID_LEVEL"] = 1

    param_list = [param_series for _ in range(5)]
    param_list = history_param + param_list
    print("param_list : \n{}".format(param_list))
    param_throughput = []
    for s, v in zip(param_list, throughput_list):
        s["TARGET"] = v
        param_throughput.append(s)
    # add new params and throughput to history_data.csv
    record_data = pd.DataFrame(param_throughput)
    record_data.to_csv("history_data.csv", index=False)
    # return params and throughput
    return param_throughput

def execute_adjust_param(n):
    # db_bench not exists in current directory
    if os.path.exists(BENCH_NAME) == False:
        print("Do not exist db_bench")
        return False, []
    # loop n times, get recommend params and then run the next params
    param = ""
    for i in range(n):
        # collect throughput and corresponding parameters
        execute_file_name = BENCH_NAME + param
        start_time = time.time()
        os.system(execute_file_name)
        end_time = time.time()
        step = (end_time - start_time) / 5
        param_throughput = collect_range_param_and_throughput(start_time, end_time, step)
        recommend = adjust(param_throughput, 2)
        print("recommend params : {}".format(recommend))
        recommend = recommend[:-1]
        param = ""
        for i in range(3):
            param = param + " " + list(recommend.index)[i] + "=" + str(recommend[i])+" "

# execute_adjust_param(2)
# s1 = pd.Series([1,2,3], index=['a','b','c'])
# s2 = pd.Series([11,22,33], index=['a','b','c'])
# s3 = pd.Series([111,222,333], index=['a','b','c'])
# df = pd.DataFrame([s1, s2])
# print(df)
# df.to_csv('test', index=False)
execute_adjust_param(2)