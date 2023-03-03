import pygame
import random
import time
from sprite import *
from settings import *
import math 

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
        self.start_timer = False
        self.elapsed_time = 0
        self.high_score = float(self.get_high_scores()[0])
    
    def get_blank_position(self, matrix):
        for row in range(len(matrix)):
            for col in range(len(matrix[0])):
                if matrix[row][col] == 0:
                    return row, col

    def matrix_to_string(self, matrix):
        return "".join(str(matrix[row][col]) for row in range(len(matrix)) for col in range(len(matrix[0])))

    def string_to_matrix(self, string):
        matrix = []
        index = 0
        for row in range(GAME_SIZE):
            matrix.append([])
            for col in range(GAME_SIZE):
                matrix[row].append(int(string[index]))
                index += 1
        return matrix
    
    def heuristic(self, state, goal):
        distance = 0
        for row in range(GAME_SIZE):
            for col in range(GAME_SIZE):
                value = state[row][col]
                if value != 0:
                    target_row = (value - 1) // GAME_SIZE
                    target_col = (value - 1) % GAME_SIZE
                    distance += abs(row - target_row) + abs(col - target_col)
        return distance


    def reconstruct_path(self, initial_state, final_state):
        current_state = final_state
        path = [current_state]
        while current_state != initial_state:
            current_state = current_state.parent
            path.append(current_state)
        path.reverse()
        return path


    def solve(self):
        initial_state = self.tiles_grid
        final_state = self.tiles_grid_completed
        open_list = []
        closed_list = set()
        g_score = {self.matrix_to_string(initial_state): 0}
        f_score = {self.matrix_to_string(initial_state): self.heuristic(initial_state, final_state)}
        open_list.append(initial_state)

        while open_list:
            current_state = min(open_list, key=lambda state: f_score[self.matrix_to_string(state)])
            if current_state == final_state:
                return self.reconstruct_path(initial_state, current_state)

            open_list.remove(current_state)
            closed_list.add(self.matrix_to_string(current_state))

            for neighbor in self.get_neighbors(current_state):
                if self.matrix_to_string(neighbor) in closed_list:
                    continue
                tentative_g_score = g_score[self.matrix_to_string(current_state)] + 1
                if self.matrix_to_string(neighbor) not in [self.matrix_to_string(state) for state in open_list]:
                    open_list.append(neighbor)
                elif tentative_g_score >= g_score[self.matrix_to_string(neighbor)]:
                    continue

                g_score[self.matrix_to_string(neighbor)] = tentative_g_score
                f_score[self.matrix_to_string(neighbor)] = tentative_g_score + self.heuristic(neighbor, final_state)

    def get_neighbors(self, matrix):
        neighbors = []
        row, col = self.get_blank_position(matrix)
        if row > 0:
            neighbor = [row - 1, col]
            new_matrix = [row[:] for row in matrix]
            new_matrix[row][col], new_matrix[neighbor[0]][neighbor[1]] = new_matrix[neighbor[0]][neighbor[1]], new_matrix[row][col]
            neighbors.append(new_matrix)
        if col > 0:
            neighbor = [row, col - 1]
            new_matrix = [row[:] for row in matrix]
            new_matrix[row][col], new_matrix[neighbor[0]][neighbor[1]] = new_matrix[neighbor[0]][neighbor[1]], new_matrix[row][col]
            neighbors.append(new_matrix)
        if row < GAME_SIZE - 1:
            neighbor = [row + 1, col]
            new_matrix = [row[:] for row in matrix]
            new_matrix[row][col], new_matrix[neighbor[0]][neighbor[1]] = new_matrix[neighbor[0]][neighbor[1]], new_matrix[row][col]
            neighbors.append(new_matrix)
        if col < GAME_SIZE - 1:
            neighbor = [row, col + 1]
            new_matrix = [row[:] for row in matrix]
            new_matrix[row][col], new_matrix[neighbor[0]][neighbor[1]] = new_matrix[neighbor[0]][neighbor[1]], new_matrix[row][col]
            neighbors.append(new_matrix)
        return neighbors



    def get_high_scores(self):
        with open("high_score.txt","r") as file:
            scores = file.read().splitlines()
        return scores
    
    def save_score(self):
        with open("high_score.txt","w") as file:
            file.write("%.3f\n" % self.high_score)

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles_grid = self.create_game()
        self.tiles_grid_completed = self.create_game()
        self.elapsed_time = 0
        self.start_timer = False
        self.start_game = False
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
        
        #Inicio do jogo
        if self.start_game:
            if self.tiles_grid == self.tiles_grid_completed:
                self.start_game = False
                if self.high_score > 0:
                    self.high_score = self.elapsed_time if self.elapsed_time < self.high_score else self.high_score
                else:
                    self.high_score = self.elapsed_time
                self.save_score()

            if self.start_timer:
                self.timer = time.time()
                self.start_timer = False
            self.elapsed_time = time.time() - self.timer

        # Embaralhamento do jogo
        if self.start_shuffle:
            self.shuffle()
            self.draw_tiles()
            self.shuffle_time += 1
            if self.shuffle_time > 120:
                self.start_shuffle = False
                self.start_game = True
                self.start_timer = True

        self.all_sprites.update()
        
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

        UIElement(710, 380, "High Score - %.3f" % (self.high_score if self.high_score > 0 else 0)).draw(self.screen)
        UIElement(825,35,"%.3f"  % self.elapsed_time).draw(self.screen)
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
                            self.solve()

game = Game()

while True:
    game.new()
    game.run() 




