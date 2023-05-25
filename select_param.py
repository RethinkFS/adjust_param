import numpy as np
import pandas as pd
from aquire_history_data import CONTINUOUS_PARAM, DISCRETE_PARAM
MAX_INT=(1<<8)-1
# 求一个target方差
def Var(data):
    return np.var(data)

# 第一次还未选择参数时选出最重要第一位参数
def PI(data_set,un_selected_param):
    # 通过单个数据项的离散值划分数据集合
    select_id = -1
    min_param_var = MAX_INT
    for i in range(len(un_selected_param)):
        param_set = dict()  # 字典的键是数值 value是数据下标索引
        for j, data in enumerate(data_set):
            if data[i] not in param_set.keys():
                param_set[data[i]] = [j]
            else:
                param_set[data[i]].append(j)
        # 求PI系数
        param_total_var = 0.0
        # print(param_set)
        for k, v in param_set.items():
            param_total_var += len(v) / len(data_set) * Var([data_set[v[a]][-1] for a in range(len(v))])
        if param_total_var < min_param_var:
            min_param_var = param_total_var
            select_id = i
    return select_id, param_total_var

# 将每个参数的条件集合方差作为列表返回
def CPI(data_set, un_selected_param):
    # 通过单个数据项的离散值划分数据集合
    result = []
    for i in range(len(un_selected_param)):
        param_set = dict()  # 字典的键是数值 value是数据下标索引
        for j, data in enumerate(data_set):
            if data[i] not in param_set.keys():
                param_set[data[i]] = [j]
            else:
                param_set[data[i]].append(j)
        # 求PI系数
        param_total_var = 0.0
        for k, v in param_set.items():
            param_total_var += len(v) / len(data_set) * Var([data_set[v[a]][-1] for a in range(len(v))])
        result.append(param_total_var)
    return result

# select n most important parameters
def select_param(history_data, n):
    if len(history_data) <= 0:
        return []
    if len(history_data[0]) < n:
        n = len(history_data[0])-1
    index_name = [index for index in history_data[0].keys()]
    selected_param = [] # 已选参数名
    un_selected_param = [i for i in range(len(history_data[0])-1)] # 去除target 未选参数下标索引

    print("select {} params".format(n))
    # 根据参数个数停止参数选择
    while len(selected_param) <= n:
        # 长度为0 选择第一个影响力最大参数
        if len(selected_param) == 0:
            target_data = [history_data[i][-1] for i in range(len(history_data))] # 目标数据
            target_var = Var(target_data)
            # 通过单个数据项的离散值划分数据集合
            select_id, min_param_var = PI(history_data, un_selected_param)
            final_val = target_var - min_param_var
            print(target_var, min_param_var, final_val)
            print("Select {0} param, param name: {1}, var:{2}".format(select_id, index_name[select_id], final_val))
        else:
            # 通过已选参数划分集合
            param_set = dict() # 字典的键是已选参数数值list value是数据下标索引list series无法hash做不了key
            for i, data in enumerate(history_data):
                selected_param_list = tuple(data[selected_param].tolist())
                if selected_param_list not in param_set.keys():
                    param_set[selected_param_list] = [i]
                else:
                    param_set[selected_param_list].append(i)
            # 固定集合 在未选择的参数中选择CPI系数最大的参数
            # 每个参数的CPI系数由所有划分集合中的最大CPI系数决定
            result = [-1 for _ in range(len(un_selected_param))]
            for _, data_set_index in param_set.items():
                data_set = [history_data[i] for i in data_set_index]
                cpi = CPI(data_set, un_selected_param)
                num = len(result)
                result = [result[i] if result[i] > cpi[i] else cpi[i] for i in range(num)]
            max_cpi = max(result)
            selected_param_index = result.index(max_cpi)
            select_id = un_selected_param[selected_param_index]
            print("Select {0} param, param name: {1}, cpi:{2}".format(select_id, index_name[select_id], max_cpi))
            # selected_param.append(index_name[select_id])
            # un_selected_param.remove(select_id)
            # 选择参数加入并从全集中删除
        selected_param.append(index_name[select_id])
        un_selected_param.remove(select_id)
        continuous_data = [param for param in selected_param if param in CONTINUOUS_PARAM]
        discrete_data = [param for param in selected_param if param in DISCRETE_PARAM]
    return selected_param, continuous_data, discrete_data

# s1 = pd.Series([2, 4, 5, 6], index=list("abcd"))
# s2 = pd.Series([2, 4, 5, 6], index=list("abcd"))
# s3 = pd.Series([3, 4, 5, 7], index=list("abcd"))
index = ["a","b"]
# data = []
# data.append(s1[index])
# data.append(s2[index])
# print(data)
# index_num = [1,2]
# index_num2 = [2,3]
# print(s1)
# print(s1[index]==s2[index])
# print(s1[index_num]==s2[index_num])
# if (s1[index]==s2[index]).all():
#     print("equal")
# else:
#     print("not equal")
#
# print(s1.tolist())
# print(np.array(s1.tolist()))
# print(len(s1))