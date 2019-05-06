import numpy as np
import os
import sys
import pickle
import datetime

from player import Machine
from snake_game import Game

save_path = os.path.join("./saved_pops/")
save_freq = 10

class Population:
    def __init__(self, model=[24, 18, 3], population=100, turn_limit=50, random_seed=None, partition=[5, 55],
                    random_select=.01, mutation_rate=.01):
        self.population_num = population
        self.population = []
        self.generation_num = 0
        self.turn_limit = turn_limit
        self.model = model
        self.random_seed = random_seed if random_seed is not None else np.random.randint(0, 2**30)
        self.partition = partition
        self.random_select = random_select
        self.mutation_rate = mutation_rate
        self._generate_generation()

    def _sort_population(self):
        self.population.sort(key=lambda x: x.calculate_fitness(), reverse=True)
        for i in self.population:
            print("<f:%f, a:%d, t:%d>" %(i.fitness, i.eaten_apples, i.iteration_number), end=" ")
        print()
        return self

    def _generate_generation(self):
        if len(self.population) < 1:
            for i in range(self.population_num):
                self.population.append(self._create_new_individual())
            return self
        else:
            self._sort_population()
            alive_border = np.sum(self.partition)
            parents = self.population[:alive_border]

            for individual in self.population[alive_border:]:
                if self.random_select > np.random.rand():
                    parents.append(individual)
            
            for individual in parents:
                if self.mutation_rate > np.random.rand():
                    individual.player.mutation(self.mutation_rate)

            while len(parents) < self.population_num:
                parent_1 = np.random.randint(len(parents))
                parent_2 = np.random.randint(len(parents))

                if parent_1 != parent_2:
                    parent_1 = parents[parent_1]
                    parent_2 = parents[parent_2]

                    child_player = parent_1.player.crossover(parent_2.player)
                    child_game = Game(player=child_player, turn_limit=self.turn_limit, seed=self.random_seed)
                    parents.append(child_game)
            
            for i in range(len(parents)):
                player = parents[i].player
                parents[i] = Game(player=player, turn_limit=self.turn_limit, seed=self.random_seed)
            self.population = parents
        self.generation_num += 1
        self.random_seed = np.random.randint(0, 2**30)

    def iterate(self):
        for individual in self.population:
            while not individual.is_game_end:
                individual.iterate()
        self._generate_generation()
    
    def _create_new_individual(self):
        player = Machine(model=self.model)
        game = Game(player=player, turn_limit=self.turn_limit, seed=self.random_seed)
        return game

if __name__ == "__main__":
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    pop = Population(turn_limit=100)
    args = sys.argv
    if "-f" in args:
        index = args.index("-f")
        saved_file = open(args[index + 1], "rb")
        pop = pickle.load(saved_file)
    
    round = float("inf")
    tour = 0
    while round != tour:
        print("Gen:", pop.generation_num)
        pop.iterate()
        tour += 1
        if (tour % save_freq) == (save_freq - 1):
            time = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
            file_name = time + "-Gen:" + str(pop.generation_num)
            save_file = open(os.path.join(save_path, file_name), "wb")
            pickle.dump(pop, save_file)
            save_file.close()