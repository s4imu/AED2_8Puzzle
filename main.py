import pygame
import random
import time
import timeit
import copy
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
        self.start_timer = False
        self.elapsed_time = 0
        self.high_score = float(self.get_high_scores()[0])

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
                            self.new()

META = [[1,2,3],[4,5,6],[7,8,0]]

class No:
	def __init__(self,estado,pai,distanciaPercorrida,custo):
		self.estado = estado
		self.pai = pai
		self.distanciaPercorrida = distanciaPercorrida
		self.custo = custo

	def __eq__ (self,outro):
		return self.estado == outro.estado
	def __repr__ (self):
		return str(self.estado)
	def getState(self):
		return self.estado

def solucionavel(lista):
  inversoes = 0
  for linha, bloco in enumerate(lista):
    if bloco == 0:
      continue
    for coluna in range(linha+1,len(lista)):
      if lista[coluna]==0:
        continue
      if bloco > lista[coluna]:
        inversoes += 1
  if inversoes % 2 == 1:
    return False
  else:
    return True

def geraInicial(estado=META[:]):
  lista = [coluna for linha in estado for coluna in linha]
  while True:
    random.shuffle(lista)
    estado = [lista[:3]]+[lista[3:6]]+[lista[6:]]
    if solucionavel(lista) and estado != META: return estado
  return 0

def localizar(estado,elemento=0):
  for linha_atual in range(3):
    for coluna_atual in range(3):
      if estado[linha_atual][coluna_atual] == elemento:
        linha = linha_atual
        coluna = coluna_atual
        return linha,coluna
    
def distanciaQuarteirao(estado1,estado2):
  distancia = 0
  fora_de_posicao = 0
  for linha in range(3):
    for coluna in range(3):
      if estado1[linha][coluna] == 0: continue
      linha_comparacao,coluna_comparacao = localizar(estado2,estado1[linha][coluna])
      if linha_comparacao != linha or coluna_comparacao != coluna: fora_de_posicao += 1
      distancia += abs(linha_comparacao-linha)+abs(coluna_comparacao-coluna)

    return distancia + fora_de_posicao


def criarNo(estado,pai,gx=0):
  hx = distanciaQuarteirao(estado,META)
  fx = gx + hx

  return No(estado,pai,gx,fx)

def inserirNoFilaPrioridades(no,fila):
  if no in fila:
    return fila
  fila.append(no)
  chave = fila[-1]
  posicao = len(fila) - 2
  while fila[posicao].custo > chave.custo and posicao >= 0:
    fila[posicao+1] = fila[posicao]
    fila[posicao] = chave
    posicao -= 1
  return fila


def moverAbaixo(estado):
  linha,coluna = localizar(estado)
  if linha < 2:
    estado[linha+1][coluna],estado[linha][coluna] = estado[linha][coluna],estado[linha+1][coluna]
  return estado

def moverAcima(estado):
  linha,coluna = localizar(estado)
  if linha > 0:
    estado[linha-1][coluna],estado[linha][coluna] = estado[linha][coluna],estado[linha-1][coluna]
  return estado

def moverDireita(estado):
  linha,coluna = localizar(estado)
  if coluna < 2:
    estado[linha][coluna+1],estado[linha][coluna] = estado[linha][coluna],estado[linha][coluna+1]
  return estado

def moverEsquerda(estado):
  linha,coluna = localizar(estado)
  if coluna > 0:
    estado[linha][coluna-1],estado[linha][coluna] = estado[linha][coluna],estado[linha][coluna-1]
  return estado

def possiveisMovimentos(no):
  #ultilizamos o deepcopy para passar uma copia do estado afim de evitar efeitos colaterais que as funcoes podem causar no estado que esta sendo passado
  estado = no.estado
  pai = no.pai

  if pai:
    estadoPai = pai.estado
  else:
    estadoPai = None

  movimentos = []

  movimentosParaCima = moverAcima(copy.deepcopy(estado))
  if movimentosParaCima != estado:
    movimentos.append(movimentosParaCima)

  movimentosParaDireita = moverDireita(copy.deepcopy(estado))
  if movimentosParaDireita != estado:
    movimentos.append(movimentosParaDireita)

  movimentosParaBaixo = moverAbaixo(copy.deepcopy(estado))
  if movimentosParaBaixo != estado:
    movimentos.append(movimentosParaBaixo)
    
  movimentosParaEsquerda = moverEsquerda(copy.deepcopy(estado))
  if movimentosParaEsquerda != estado:
    movimentos.append(movimentosParaEsquerda)

  return movimentos

def buscaResolucao(numMaxTentativas,noInicial):
  print(noInicial,":")

  numMovimentos = 0
  movimentos = [noInicial]

  while movimentos:

      no = movimentos.pop(0)

      if no.estado == META:
          solucao = []

          while True:
            solucao.append(no.estado)
            no = no.pai
            if not no: break 
               
          solucao.reverse()
          return solucao, numMovimentos
    
      numMovimentos += 1

      if(numMovimentos % (numMaxTentativas/10)) == 0: print(numMovimentos,end="....")
      if(numMovimentos>numMaxTentativas): break

      movimentosPossiveis = possiveisMovimentos(no) 

      for movimento in movimentosPossiveis:
        inserirNoFilaPrioridades(criarNo(movimento,no,no.distanciaPercorrida+1),movimentos)

  return 0, numMovimentos 

def puzz8(maxProfundidade,numAmostras):
  tempos = []
  solucionados = []
  solucoes = []
  naoSolucionados = []
  numSolucionados = 0
  numNaoSolucionados = 0
  for i in range(numAmostras):
      noInicial = criarNo(geraInicial(),None)
      start_time = timeit.default_timer()
      resolucao,numMovimentos = buscaResolucao(maxProfundidade,noInicial)
      tempo = timeit.default_timer() - start_time

      if resolucao:
        solucoes.append(resolucao)
        print("\nSolucionado em {} e {} movimentos".format(tempo,numMovimentos))
        tempos.append(tempo)
        solucionados.append((noInicial.estado,numMovimentos))
        numSolucionados += 1
      else: 
        print("\nFalhou em {} e {} movimentos".format(tempo,numMovimentos))
        naoSolucionados.append((noInicial.estado,numMovimentos))
        tempos.append(None)
        numNaoSolucionados += 1

  print("Solucionados {} e nao solucionados {}".format(numSolucionados,numNaoSolucionados))
  return tempos,solucionados,naoSolucionados, numSolucionados, numNaoSolucionados 

solve = puzz8(3000,10)
game = Game()

while True:
    game.new()
    game.run() 




