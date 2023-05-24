import numpy as np
import pandas as pd
from aquire_history_data import CONTINUOUS_PARAM, DISCRETE_PARAM, CONTINUOUS_PARAM_RANGE, DISCRETE_PARAM_RANGE
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

class gauss:
    def __init__(self, data, param):
        self.datas = data
        self.params = param
        self.param_data_array = np.array([data_series[param].tolist() for data_series in data])
        self.target = np.array([target[-1] for target in data])
        print(self.param_data_array)
        print(self.target)

    def train_model(self):
        # 核函数
        kernel = C(0.1, (0.001, 0.1)) * RBF(0.5, (1e-4, 10))
        # 高斯模型
        self.reg = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, alpha=0.1)
        print(self.param_data_array)
        print(self.target)
        # 训练模型
        self.reg.fit(self.param_data_array, self.target)

    def recommend(self):
        # 训练模型
        self.train_model()
        # 在最好的参数附近进行修改预测
        max_target_index = np.argmax(self.target)
        max_param = self.datas[max_target_index]
        recommend_param = max_param[:-1]
        max_target = max_param[-1]
        res = recommend_param
        # 调参顺序按照选择参数的重要性进行调参
        for param in self.params:
            # 离散参数尝试遍历值
            if param in DISCRETE_PARAM:
                variable_range = DISCRETE_PARAM_RANGE[param]
                variable_range = [value.value for value in variable_range]
            # 连续参数尝试按照比例遍历范围
            else:
                min_v, max_v = CONTINUOUS_PARAM_RANGE[param]["min"], CONTINUOUS_PARAM_RANGE[param]["max"]
                interval = (max_v-min_v) * 0.05
                now_v = recommend_param[param]
                variable_range = [(now_v + i * interval) for i in range(-10, 11) if i != 0]
                variable_range = [num for num in variable_range if num >= min_v and num <= max_v]
            # 调整参数
            for value in variable_range:
                if max_param[param] == value:
                    continue
                recommend_param[param] = value
                predict_x = np.array(recommend_param[self.params].tolist()).reshape(1, -1)
                output, err = self.reg.predict(predict_x, return_std=True)
                if output > max_target:
                    print(
                        "now the predicted {} value is {}, between {} and {}".format(param, output,
                                            (1 - 1.96 * err) * output, (1 + 1.96 * err) * output))
                    res = recommend_param
                    max_param = output
        return res

# xset, yset = np.meshgrid(np.arange(1, 6, 0.5), np.arange(1, 6, 0.5))
# print(xset)
# print(yset)
# print(np.c_[xset.ravel(), yset.ravel()])