import torch
import torch.nn as nn

# 三层全连接网络用于连续变量回归
class FullyConnectedNuralNetwork(nn.Module):
    def __init__(self, n):
        super(FullyConnectedNuralNetwork,self).__init__()
        self.hidden1=nn.Sequential(
                nn.Linear(in_features=-1,out_features=100,bias=True),
                nn.ReLU())
        self.hidden2=nn.Sequential(
                nn.Linear(in_features=100,out_features=100,bias=True),
                nn.ReLu())
        self.hidden3=nn.Sequential(
                nn.Linear(in_features=100,out_features=50,bias=True),
                nn.ReLU())
        self.predict=nn.Sequential(
                nn.Linear(in_features=50,out_features=1,bias=True),
                nn.ReLU())
    def forward(self,x):
        x=self.hidden1(x)
        x=self.hidden2(x)
        x=self.hidden3(x)
        x=self.predict(x)
        return x

def adjust_continuous_param(continuous_param, data):
    continuous_data = [d[continuous_param].tolist() for d in data]

