import sys
import numpy as np
np.random.seed(0)
print("NumPy version:", np.__version__)

X = [[1, 4.1, -3.5, 2],
    [0.7, 1.3, -0.2, 0.9],
    [2.0, -1.0, 0.5, -0.9]]

weight1 = [[0.7, 1.3, -0.2, 0.9],
         [2.0, -1.0, 0.5, -0.9],
         [0.1, -1.3, 1.2, -0.1]]
bias1 = [0.3, 0.8, 1.1]
weight2 = [[0.7, 1.3, -0.2],
         [2.0, -1.0, 0.5],
         [0.1, -1.3, -0.1]]
bias2 = [0.3, 0.8, 1.1]
weight3 = [[0.7, 1.3],
         [2.0, 0.5],
         [-1.3, -0.1]]
bias3 = [0.3, 1.1]

# output = []
# for w, b in zip(weight, bias):
#     res = 0
#     for i1, w1 in zip(inputs, w):
#         res += i1*w1
#     output.append(res)
# print([round(x,4) for x in output])

# layer1 = np.dot(X, np.array(weight1).T) + bias1
# print(layer1)
# layer2 = np.dot(layer1, np.array(weight2).T) + bias2
# print(layer2)
# layer3 = np.dot(layer2, np.array(weight3)) + bias3
# print(layer3)

print(np.random.randn(5,4))
class Layer:
    def __init__(self, n_input, n_neuron):
        self.weight = np.random.randn(n_input, n_neuron)
        self.bias = np.zeros((1, n_neuron))
    def forward(self, inputs):
        self.output = np.dot(inputs, self.weight) + self.bias

l1 = Layer(4,6)
l2 = Layer(6,3)
l3 = Layer(3,2)
l1.forward(X)
l2.forward(l1.output)
l3.forward(l2.output)
# print(l1.output)
# print(l2.output)
# print(l3.output)

