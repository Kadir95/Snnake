import numpy as np
import sys
import copy

from neuron import Neuron

class Network:
    def __init__(self, model=[2, 2], act_func="sigmoid"):
        if len(model) < 2:
            print("model at least has to have two positive integer value")
            raise AttributeError()
        
        self.input_num = copy.deepcopy(model).pop(0)
        self.model = model
        self.act_func = act_func

        # Creates self.layers attribute and creates perceptrons for each layer
        # as mentioned in model variable.
        self._init_layers()

    # Initialize self.layers attribute and creates perceptrons
    def _init_layers(self):
        self.layers = []
        input_number = self.input_num
        for node_num, layer_num in zip(self.model, range(len(self.model))):
            layer = []
            for i in range(node_num):
                layer.append(Neuron(input_num=input_number))
            self.layers.append(layer)
            input_number = node_num
    
    def mutate(self, mutate_rate):
        for layer_num in range(len(self.layers)):
            for node_num in range(len(self.layers[layer_num])):
                self.layers[layer_num][node_num].mutate(mutate_rate)
        return self
    
    def import_weights(self, weights):
        raise NotImplementedError()
    
    def export_weights(self):
        raise NotImplementedError()

    def crossover(self, network):
        new_network = copy.deepcopy(self)
        for layer_num in range(len(self.layers)):
            for node_num in range(len(self.layers[layer_num])):
                new_network.layers[layer_num][node_num] = self.layers[layer_num][node_num].crossover(network.layers[layer_num][node_num])
        return new_network

    def clone(self):
        return copy.deepcopy(self)

    def output(self, input_arr):
        pre_output = input_arr
        for nodes in self.layers:
            next_output = []
            for node in nodes:
                output = node.output(pre_output)
                next_output.append(output)
            pre_output = np.array(next_output)
        return pre_output
        
if __name__ == "__main__":
    network = Network(model=[2, 50, 50, 3])
    print(network.output(np.array([0, 0])))
    print(network.output(np.array([0, 0])))
    network.mutate(.1).mutate(.5)
    print(network.output(np.array([0, 0])))