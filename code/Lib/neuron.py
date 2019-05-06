import numpy as np
import copy

def redu(x):
    return x if x > 0 else 0

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def tanh(x):
    return (np.exp(x) - np.exp(-x))/(np.exp(x) + np.exp(-x))

class Neuron:
    def __init__(self, input_num=1, act_func=redu, normal_scale=5):
        self.weight_array = np.random.rand(input_num + 1)
        self.x0 = 1
        self.act_func = act_func
        self.input_num = input_num
        self.normal_scale = normal_scale

    def output(self, data):
        x_array = np.append(self.x0, data)
        result = np.dot(x_array, np.transpose(self.weight_array))
        return self.act_func(result)
    
    def crossover(self, neuron):
        cut_loc = np.random.randint(0, len(self.weight_array))
        new_neuron = Neuron(input_num=self.input_num, act_func=self.act_func)
        new_neuron.weight_array = np.append(self.weight_array[:cut_loc], neuron.weight_array[cut_loc:])
        return new_neuron

    def mutate(self, mutation_rate):
        for i in range(len(self.weight_array)):
            if np.random.random() < mutation_rate:
                self.weight_array[i] += np.random.normal(scale=self.normal_scale)
        return self
    
    def clone(self):
        return copy.deepcopy(self)
    
    def import_weight(self, weight):
        self.weight_array = weight
    
    def export_weight(self):
        return self.weight_array
    
    def __str__(self):
        return "<Input_num:%s, weight_array:%s>" %(len(self.weight_array) - 1, str(self.weight_array))