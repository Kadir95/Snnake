import pygame
import sys
import os
import pickle
import pprint
import time
import random

sys.path.append("./Lib/")
from player import Dummy
from population import Population
#from Lib.snake_game import Empty_Cell, Apple, Wall, Snake_Body, Game_Object
import snake_game as sg

pop_path = os.path.join("./pops/")

class Snnake(object):
    def __init__(self, pop, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
        """
        pygame.init()
        pygame.display.set_caption("Snnake")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.pop = pop

        game = self.pop.population[0]
        player = game.player

        game = sg.Game(player=player, turn_limit=100)

        print(game.is_game_end)

        self.snnake_play = SnnakePlay(self.screen, (0, 0, width, height), game)

    def run(self):
        """The mainloop
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        running = True
        while running:
            # milliseconds = self.clock.tick(self.fps)
            # self.playtime += milliseconds / 1000.0
            # self.draw_text("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
            #                self.clock.get_fps(), " "*5, self.playtime))
            self.snnake_play.draw(event=pygame.event.get())
            time.sleep(.1)
            self.snnake_play.iterate()

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

        pygame.quit()

    def draw_text(self, text):
        """Center text in window
        """
        fw, fh = self.font.size(text) # fw: font width,  fh: font height
        surface = self.font.render(text, True, (0, 255, 0))
        # // makes integer division in python3
        self.screen.blit(surface, ((self.width - fw) // 2, (self.height - fh) // 2))

class SnnakePlay():
    def __init__(self, display, coor, game):
        self.display = display
        self.coor = coor
        self.game = game
        self.font = pygame.font.SysFont('mono', 30)

        # Calculation of one cube's pixel size
        x, y = coor[2], coor[3]
        game_x, game_y = game.shape[0], game.shape[1]
        pix_x, pix_y = (x // game_x), (y // game_y)

        print(x, y)
        print(game_x, game_y)
        print(pix_x, pix_y)

        self.cube_size = pix_x if pix_y > pix_x else pix_y

        print(self.cube_size)
    
    def iterate(self):
        self.game.iterate()

    def _draw_text(self, font, text, color, x, y):
        surface = font.render(text, True, color)
        self.display.blit(surface, (x, y))

    def _draw_cube(self, x, y, color):
        pygame.draw.rect(self.display, color, (x, y, self.cube_size, self.cube_size))

    def _draw_apple(self, x, y):
        self._draw_cube(x, y, (255, 0, 0))
    
    def _draw_wall(self, x, y):
        self._draw_cube(x, y, (200, 200, 200))

    def _draw_snake(self, x, y):
        self._draw_cube(x, y, (255, 255, 255))

    def _info_panel(self, text, color, no, font=None):
        x = self.game.shape[0] * self.cube_size + self.cube_size
        y = self.cube_size * no
        self._draw_text(font or self.font, text, color, x, y)

    def draw(self, event=None):
        map = self.game.map
        
        eaten_apple_str = "Eaten Apple: %d" %(self.game.eaten_apples)
        self._info_panel(eaten_apple_str, (255, 255, 255), 1)

        turn_num_str = "Turn: %d" %(self.game.iteration_number)
        self._info_panel(turn_num_str, (255, 255, 255), 2)

        starving_turn_str = "Starving Turn: %d" %(self.game.starving_turn)
        self._info_panel(starving_turn_str, (255, 100, 100), 3)

        if self.game.is_game_end and not hasattr(self, "end_button"):
            end_str = "Game Over"
            font = pygame.font.SysFont("mono", 50, bold=True)
            #self._info_panel(end_str, (255, 0, 0), 14, font=font)
            close = lambda mouse_pos: sys.exit(0)
            end_coor = (self.game.shape[0] * self.cube_size + self.cube_size, self.cube_size * 14, self.cube_size * 6, self.cube_size)
            self.end_button = Button(self.display, text="Game Over", text_color=(255, 255, 255), font=font, coor=end_coor, color=(200, 0, 0), func=close)

        if hasattr(self, "end_button"):
            for e in event:
                self.end_button.check(e)
            self.end_button.draw()

        for y_t in range(len(map)):
            for x_t in range(len(map[y_t])):
                current_tile = map[y_t][x_t]

                x = self.coor[0] + x_t * self.cube_size
                y = self.coor[1] + y_t * self.cube_size

                if str(current_tile) != " ":
                    if str(current_tile) == "A":
                        self._draw_apple(x, y)
                    elif str(current_tile) == "W":
                        self._draw_wall(x, y)
                    elif str(current_tile) == "S":
                        self._draw_snake(x, y)

class Button():
    def __init__(self, display, text="New Button", text_color=(255, 255, 255), font=None, coor=(10, 10, 200, 70), color=(127, 127, 127), func=None):
        self.display = display
        self.text = text
        self.text_color = text_color
        self.font = font or pygame.font.SysFont('mono', 12)
        self.coor = coor
        self.color = color
        self.func = func
    
    def draw(self):
        fw, fh = self.font.size(self.text) # fw: font width,  fh: font height
        surface = self.font.render(self.text, True, self.text_color)
        
        pygame.draw.rect(self.display, self.color, self.coor)
        self.display.blit(surface, (self.coor[0] + ((self.coor[2] - fw) // 2), self.coor[1] + ((self.coor[3] - fh) // 2)))
    
    def on_click(self, event):
        # Mouse position may pass
        if self.func is not None:
            self.func(event.pos)

    def check(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.coor[0] + self.coor[2] > event.pos[0] > self.coor[0] and self.coor[1] + self.coor[3] > event.pos[1] > self.coor[1]:
                    self.on_click(event)
        

if __name__ == '__main__':
    # call with width of window and fps
    file_name = "./pops/2019_05_02-09_10_15-Gen:439"
    if "-f" in sys.argv:
        index = sys.argv.index("-f")
        file_name = sys.argv[index + 1]
    pop_file_path = os.path.join(file_name)
    pop_file = open(pop_file_path, "rb")
    pop = pickle.load(pop_file)
    Snnake(pop, 1200, 800).run()
