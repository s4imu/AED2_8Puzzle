import pygame
import random
import time
from sprite import *
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) #cria uma nova janela com as dimensões
        pygame.display.set_caption(title) #define o titulo da janela do jogo
        self.clock = pygame.time.Clock() #controla o tempo do jogo
        self.shuffle_time = 0
        self.start_shuffle = False
        self.previous_choice = ""
        self.start_game =  False
        self.start_timer = 0
        self.elapsed_time = 0

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles_grid = self.create_game()
        self.tiles_grid_completed = self.create_game()
        self.buttons_list = []
        self.buttons_list.append(Button(775,100,200,50,"Shuffle",WHITE,BLACK))
        self.buttons_list.append(Button(775,170,200,50,"Solve",WHITE,BLACK))
        self.draw_tiles()
    
    def shuffle(self):
        possible_moves = []
        for row, tiles in enumerate(self.tiles):
            for col, tile in enumerate(tiles):
                if tile.text == "empty":
                    if tile.right():
                        possible_moves.append("right")
                    if tile.left():
                        possible_moves.append("left")
                    if tile.up():
                        possible_moves.append("up")
                    if tile.down():
                        possible_moves.append("down")
                    break
            if len(possible_moves) > 0:
                break
        
        if self.previous_choice == "right":
            possible_moves.remove("left") if "left" in possible_moves else possible_moves
        if self.previous_choice == "left":
            possible_moves.remove("right") if "right" in possible_moves else possible_moves
        if self.previous_choice == "up":
            possible_moves.remove("down") if "down" in possible_moves else possible_moves
        if self.previous_choice == "down":
            possible_moves.remove("up") if "up" in possible_moves else possible_moves
            
        choice = random.choice(possible_moves)
        self.previous_choice = choice
        if choice == "right":
            self.tiles_grid[row][col], self.tiles_grid[row][col+1] = self.tiles_grid[row][col+1], self.tiles_grid[row][col]
        elif choice == "left":
            self.tiles_grid[row][col], self.tiles_grid[row][col-1] = self.tiles_grid[row][col-1], self.tiles_grid[row][col]
        elif choice == "up":
            self.tiles_grid[row][col], self.tiles_grid[row-1][col] = self.tiles_grid[row-1][col], self.tiles_grid[row][col]
        elif choice == "down":
            self.tiles_grid[row][col], self.tiles_grid[row+1][col] = self.tiles_grid[row+1][col], self.tiles_grid[row][col]

    def draw_tiles(self):
        self.tiles =[]
        for row, x in enumerate(self.tiles_grid):
            self.tiles.append([])
            for col, tile  in enumerate(x):
                if tile !=0:
                    self.tiles[row].append(Tile(self,col,row,str(tile)))
                else:
                    self.tiles[row].append(Tile(self,col,row,"empty"))

    def create_game(self):
        grid=[]
        number=1
        for x in range(GAME_SIZE):
            grid.append([])
            for y in range(GAME_SIZE):
                grid[x].append(number)
                number += 1
        grid[-1][-1]=0
        return grid

    def run(self):
        self.playing = True #cria um jogo
        while self.playing:

            self.clock.tick(FPS) #limita a tatxa de atualização do jogo
            #chama os metodos que caracterizam o jogo
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        if self.start_shuffle:
            self.shuffle()
            self.draw_tiles()
            self.shuffle_time += 1
            if self.shuffle_time > 120:
                self.start_shuffle = False

    def draw_grid(self):
        for row in range(-1, GAME_SIZE*TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY,(row,0),(row,GAME_SIZE*TILESIZE))
        
        for col in range(-1, GAME_SIZE*TILESIZE, TILESIZE):
            pygame.draw.line(self.screen,LIGHTGREY,(0,col),(GAME_SIZE*TILESIZE,col))

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.all_sprites.draw(self.screen)
        self.draw_grid()
        for button in self.buttons_list:
            button.draw(self.screen)

        pygame.display.flip()

    def events(self):
        for event in pygame.event.get(): #percorre os eventos do jogo em busca de um evento de saida
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
            
            if event.type== pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for row, tiles in enumerate(self.tiles):
                    for col, tile in enumerate(tiles):
                        if tile.click(mouse_x,mouse_y):
                            if tile.right() and self.tiles_grid[row][col+1]==0:
                                self.tiles_grid[row][col], self.tiles_grid[row][col+1] = self.tiles_grid[row][col+1], self.tiles_grid[row][col]
                            
                            if tile.left() and self.tiles_grid[row][col-1]==0:
                                self.tiles_grid[row][col], self.tiles_grid[row][col-1] = self.tiles_grid[row][col-1], self.tiles_grid[row][col]
                            
                            if tile.up() and self.tiles_grid[row-1][col]==0:
                                self.tiles_grid[row][col], self.tiles_grid[row-1][col] = self.tiles_grid[row-1][col], self.tiles_grid[row][col]
                            
                            if tile.down() and self.tiles_grid[row+1][col]==0:
                                self.tiles_grid[row][col], self.tiles_grid[row+1][col] = self.tiles_grid[row+1][col], self.tiles_grid[row][col]
                                                         
                            self.draw_tiles()
                for button in self.buttons_list:
                    if button.click(mouse_x,mouse_y):
                        if button.text == "Shuffle":
                            self.shuffle_time = 0
                            self.start_shuffle = True
                        if button.text == "Solve":
                            self.new()

game = Game()

while True:
    game.new()
    game.run() 




