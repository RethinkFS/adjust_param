# adjust params system
from aquire_history_data import history_data
from select_param import select_param
from gauss_regression import gauss


def adjust(data, n):
    all_param, continuous_param, discrete_param = select_param(data, n)
    print(all_param, continuous_param, discrete_param, sep='\n')
    # gauss_regression
    gauss_regress = gauss(data, all_param)
    return gauss_regress.recommend()
    # # continuous variable
    # adjust_continuous_param(continuous_param, data)
    # # discrete variable
    #
    # # aquire final params
# recommend = adjust(4)
# print(recommend)