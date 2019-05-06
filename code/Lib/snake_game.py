import numpy as np

from player import Player

def loc_sum(loc1, loc2):
    return (loc1[0] + loc2[0], loc1[1] + loc2[1])

class Game_Object:
    def __init__(self, loc=(0, 0), game=None):
        self.loc = loc      # loc:(x, y)
        self.game = game    # Game instance

    def __str__(self):
        raise NotImplementedError()

class Empty_Cell(Game_Object):
    def __str__(self):
        return " "

class Snake_Body(Game_Object):
    def __str__(self):
        return "S"

class Apple(Game_Object):
    def __str__(self):
        return "A"

class Wall(Game_Object):
    def __str__(self):
        return "W"

class Game:
    def __init__(self, shape=(15, 15), player=None, seed=None, turn_limit=float("inf")):
        self.snake = []
        self.apples = []
        self.shape = shape
        self.map = []
        self.is_game_end = False
        self.player = player
        self.player_direction = 1
        self.eaten_apples = 0
        self.iteration_number = 0
        self.fitness = .0
        self.turn_limit = turn_limit
        self.starving_turn = 0

        if not isinstance(player, Player):
            raise ValueError(Player)

        if isinstance(seed, (int)) or seed is None:
            self.random_state = np.random.RandomState(seed)
        else:
            print("Seed must be an int")
            self.random_state = np.random.RandomState()
        
        for y in range(shape[1]):
            temp = []
            for x in range(shape[0]):
                if (y == 0 or y == self.shape[1] - 1) or (x == 0 or x == self.shape[0] - 1):
                    temp.append(Wall(loc=np.array((x, y)), game=self))
                else:
                    temp.append(Empty_Cell(loc=np.array((x, y)), game=self))
            self.map.append(temp)

        self.directions = [
            np.array((0, 1)),     # 0, back
            np.array((-1, 1)),    # 1, left back
            np.array((-1, 0)),    # 2, left
            np.array((-1, -1)),   # 3, left front
            np.array((0, -1)),    # 4, front
            np.array((1, -1)),    # 5, right front
            np.array((1, 0)),     # 6, right
            np.array((1, 1))      # 7, right back
        ]

        self._init_game()

    def _generate_random_loc(self):
        return np.array((self.random_state.randint(0, self.shape[0]),
                self.random_state.randint(0, self.shape[1])))

    def _generate_random_unused_loc(self):
        rand_loc = self._generate_random_loc()
        while not isinstance(self.map[rand_loc[1]][rand_loc[0]], Empty_Cell):
        #while not str(self.map[rand_loc[1]][rand_loc[0]]) == " ":
            rand_loc = self._generate_random_loc()
        return rand_loc

    def _init_game(self):
        for i in range(3):
            body = Snake_Body(loc=np.array((i + 1, 1)), game=self)
            self.snake.append(body)
            self.map[1][i + 1] = body
        
        rand_loc = self._generate_random_unused_loc()
        self.map[rand_loc[1]][rand_loc[0]] = Apple(loc=rand_loc, game=self)

    def _sense_environment(self):
        # vision[0] = back
        # vision[1] = left back
        # vision[2] = left
        # vision[3] = left front
        # vision[4] = front
        # vision[5] = right front
        # vision[6] = right
        # vision[7] = right back

        player_current_loc = self.snake[len(self.snake) - 1].loc
        vision = np.zeros((8, 3))
        for i in range(8):
            direction = self.directions[i]
            observation_loc = player_current_loc + direction
            food = None
            body = None
            wall = None
            while (observation_loc >= 0).all() and (observation_loc[0] < self.shape[0] and observation_loc[1] < self.shape[1]):
                loc_cell = self.map[observation_loc[1]][observation_loc[0]]
                
                if food is None and isinstance(loc_cell, Apple):
                #if food is None and str(loc_cell) == "A":
                    food = np.sum(np.abs(observation_loc - player_current_loc))
                elif body is None and isinstance(loc_cell, Snake_Body):
                #elif body is None and str(loc_cell) == "S":
                    body = np.sum(np.abs(observation_loc - player_current_loc))
                elif wall is None and isinstance(loc_cell, Wall):
                #elif wall is None and str(loc_cell) == "W":
                    wall = np.sum(np.abs(observation_loc - player_current_loc))
                observation_loc += direction
            vision[i, 0] = food if food is not None else -1
            vision[i, 1] = body if body is not None else -1
            vision[i, 2] = wall if wall is not None else -1
        return vision
                
    def _sense_relative_vision(self):
        vision = self._sense_environment()
        return np.roll(vision, -2 * self.player_direction, axis=0)
    
    def _get_player_decision(self):
        vision = self._sense_relative_vision()
        player_decision = self.player.make_decision(vision, self)

        if player_decision == 1:
            player_decision = self.player_direction - 1 % 4
        elif player_decision == 3:
            player_decision = self.player_direction + 1 % 4
        else:
            player_decision = self.player_direction

        self.player_direction = player_decision
        return player_decision

    def calculate_fitness(self):
        self.fitness = self.eaten_apples ** 2 * float(self.iteration_number / 40)
        return self.fitness

    def iterate(self):
        if self.is_game_end:
            return
        self.iteration_number += 1
        self.starving_turn += 1

        player_decision = self._get_player_decision()
        player_current_loc = self.snake[len(self.snake) - 1].loc
        next_loc = player_current_loc + self.directions[(4 + player_decision * 2) % 8]

        # Out of map
        if (next_loc < 0).any():
            self.is_game_end = True
            self.calculate_fitness()
            return
        if next_loc[0] >= self.shape[0] or next_loc[1] >= self.shape[1]:
            self.is_game_end = True
            self.calculate_fitness()
            return

        # Wall or snake body
        next_loc_cell = self.map[next_loc[1]][next_loc[0]]
        if isinstance(next_loc_cell, (Wall, Snake_Body)):
        #if str(next_loc_cell) in ["W", "S"]:
            self.is_game_end = True
            self.calculate_fitness()
            return
        
        # Apple
        if isinstance(next_loc_cell, Apple):
        #if str(next_loc_cell) == "A":
            next_loc_cell = Snake_Body(loc=next_loc, game=self)
            self.snake.append(next_loc_cell)
            self.map[next_loc[1]][next_loc[0]] = next_loc_cell
            self.eaten_apples += 1
            
            # Reset starving turn
            self.starving_turn = 0

            # New apple
            rand_loc_apple = self._generate_random_unused_loc()
            self.map[rand_loc_apple[1]][rand_loc_apple[0]] = Apple(loc=rand_loc_apple, game=self)
            self.apples.append(self.map[rand_loc_apple[1]][rand_loc_apple[0]])
            self.calculate_fitness()
            return
        
        # Empty
        next_loc_cell = Snake_Body(loc=next_loc, game=self)
        self.snake.append(next_loc_cell)
        self.map[next_loc[1]][next_loc[0]] = next_loc_cell
        tail = self.snake.pop(0)
        self.map[tail.loc[1]][tail.loc[0]] = Empty_Cell(loc=tail.loc, game=self)
        self.calculate_fitness()

        if self.starving_turn >= self.turn_limit:
            self.is_game_end = True
            return

if __name__ == "__main__":
    from player import Human, Machine
    human= Human()
    game = Game(player=human, turn_limit=100)
    while not game.is_game_end:
        print("-------\nEaten apples:%d, Snake len:%d, Iter:%d, S_turn:%d\n" %(game.eaten_apples,
            len(game.snake), game.iteration_number, game.starving_turn))
        for y in game.map:
            for x in y:
                print(x, end= " ")
            print()
        game.iterate()