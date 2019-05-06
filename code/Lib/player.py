import numpy as np
import time
from network import Network
import copy

class Player:
    def __init__(self):
        pass
    
    def make_decision(self, vision, game):
        raise NotImplementedError()

class Human(Player):
    def make_decision(self, vision, game):
        print(vision)
        print("Make decision (1: left, 2: straight, 3: right)")
        decision = 0
        while decision not in [1, 2, 3]:
            try:
                decision = int(input())
            except:
                pass
        return decision

class Dummy(Player):
    def make_decision(self, vision, game):
        return 2

class Machine(Player):
    def __init__(self, model=[24, 18, 18, 3], sleep=0):
        self.brain = Network(model=model)
        self.sleep = sleep
    
    def make_decision(self, vision, game):
        input_arr = vision.ravel()
        output = self.brain.output(input_arr)
        max_index = np.argmax(output)
        time.sleep(self.sleep)
        return max_index + 1

    def crossover(self, player):
        new_player = copy.deepcopy(self)
        new_player.brain = self.brain.crossover(player.brain)
        return new_player
    
    def mutation(self, mutation_rate):
        self.brain.mutate(mutation_rate)
        return self
