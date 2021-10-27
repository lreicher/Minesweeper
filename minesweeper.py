import pygame
from pygame.locals import *
from random import random
from os import system, name

# game setup
FPS = 30

# colors
PUMPKIN     = (247, 120, 22)
DEEPSPACE   = (58, 96, 110)
YELLOW      = (155, 155, 0)
RED         = (155,   0,   0)
GREEN       = (  0, 155,   0)
LIGHT_GREEN = (202, 249, 185)
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
OFFWHITE    = (255, 230, 200)
CELL_OUTER  = (128, 132, 140)
CELL_INNER  = (158, 163, 173)
BLUE        = (0,0,255)
PURPLE      = (162, 40, 255)
ORANGE      = (255, 102, 0)
PINK        = (230, 0, 126)
YELLOW      = (255, 204, 0)
TURQUOISE   = (64, 224, 208)


class Sim():
    def __init__(self, gridSize, cellSize=(50,50)):
        # Sim Properties
        self.gridSize = gridSize
        self.cellSize = cellSize
        self.setup()
        # Pygame Boilerplate
        self.size = (self.gridSize[0] * self.cellSize[0], self.gridSize[1] * self.cellSize[1])
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill(BLACK)

        self.focus_cell = None
        self.grid_view = False

    def setup(self):
        self.grid = Grid(self.gridSize, self.cellSize)

    def update(self):
        self.handleEvents()
        self.draw()
        self.hasWon()

    def draw(self):
        self.grid.draw(self.screen)
        if self.focus_cell is not None:
           self.focus_cell.draw_hover(self.screen)
        if self.grid_view: self.grid.draw_gridlines(self.screen)

    def handleEvents(self):
        x,y = pygame.mouse.get_pos()
        cell = self.grid.get_cell((x,y))
        mouse = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                elif event.key == K_g:
                    self.grid_view = not self.grid_view
                    print("grid view: " + str(self.grid_view))
                elif event.key == K_d:
                    #self.grid.draw_bombs()
                    pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if cell.bomb:
                        self.hasLost()
                    else:
                        if cell.bombs == 0:
                            neighborhood = self.grid.get_zero_neighborhood(cell)
                            self.grid.make_visible(neighborhood)
                        else:
                            self.grid.make_visible([cell])
                elif event.button == 3:
                    if not cell.visible: cell.flag = not cell.flag
        self.focus_cell = cell

    def wait(self, img, x, y):
        pygame.event.clear()
        while True:
            self.screen.blit(img, (x, y))
            pygame.display.flip()
            event = pygame.event.wait()
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                return

    def hasWon(self):
        if len(self.grid.bombs) >= self.grid.numNotVisible:
            font = pygame.font.SysFont('freesansbold.ttf', 72)
            img = font.render('You Won!', True, BLUE)
            x,y = self.size
            x = x//2
            y = y//2
            #self.screen.blit(img, (x, y))
            self.wait(img, x, y)
            self.setup()

    def hasLost(self):
        font = pygame.font.SysFont('freesansbold.ttf', 72)
        img = font.render('You Lost!', True, RED)
        x,y = self.size
        x = x//2
        y = y//2
        #self.screen.blit(img, (x, y))
        self.grid.draw_bombs()
        self.grid.draw(self.screen)
        pygame.display.flip()
        self.wait(img, x, y)
        self.setup()




class Cell():
    def __init__(self, pos, size, cellpos, bomb):
        self.hover_color = OFFWHITE
        self.box = pygame.Rect(pos, size)
        self.innerbox = pygame.Rect(pos, (int(size[0]//1.1), int(size[1]//1.1)))
        self.innerbox.center = self.box.center
        self.flagbox = pygame.Rect(pos, (int(size[0]//1.4), int(size[1]//1.4)))
        self.flagbox.center = self.box.center
        self.cellpos = cellpos
        self.flag = False
        self.bomb = bomb
        self.bombs = 0
        self.text_surface_obj = None
        self.text_rect_obj = None
        self.visible = False

    def draw(self, screen):
        if self.flag and (self.bombs != -1 or not self.visible):
            pygame.draw.line(screen, RED, self.flagbox.topleft, self.flagbox.bottomright, 5)
            pygame.draw.line(screen, RED, self.flagbox.bottomleft, self.flagbox.topright, 5)
        else:
            if self.visible:
                if self.bombs == -1:
                    pygame.draw.rect(screen, CELL_OUTER, self.box)
                    pygame.draw.rect(screen, CELL_INNER, self.innerbox)
                else:
                    pygame.draw.rect(screen, WHITE, self.box)
                if self.bombs != 0:
                    screen.blit(self.text_surface_obj, self.text_rect_obj)
            else:
                pygame.draw.rect(screen, CELL_OUTER, self.box)
                pygame.draw.rect(screen, CELL_INNER, self.innerbox)


    def draw_hover(self, screen):
        pygame.draw.line(screen, BLACK, self.box.topleft,self.box.topright)
        pygame.draw.line(screen, BLACK, self.box.topleft,self.box.bottomleft)
        pygame.draw.line(screen, BLACK, self.box.bottomleft,self.box.bottomright)
        pygame.draw.line(screen, BLACK, self.box.topright,self.box.bottomright)


class Grid():
    def __init__(self, gridSize, cellSize, pos=(0,0)):
        self.pos = pos
        self.gridSize = gridSize
        self.cellSize = cellSize
        self.cells = {}
        self.bombs = []
        # Pygame Text
        self.font_obj = pygame.font.Font('freesansbold.ttf', 12)
        for x in range(self.gridSize[0]):
            for y in range(self.gridSize[1]):
                p = (x * cellSize[0], y * cellSize[1])
                bomb = random() > 0.80
                cell = Cell(p, cellSize, (x,y), bomb)
                self.cells[(x, y)] = cell
                if bomb: self.bombs.append(cell)
        self.get_bombs()
        self.numNotVisible = len(self.cells)
        self.numBombs = len(self.bombs)

    def get_cell(self, pixel_pos):
        return self.cells[int(pixel_pos[0] / self.cellSize[0]), int(pixel_pos[1] / self.cellSize[1])]

    def setCellColor(self, pos, color):
        self.cells[pos].setColor(color)

    def draw(self, screen):
        for cell in self.cells.values():
            cell.draw(screen)

    def draw_gridlines(self, screen):
        for i in range(0, self.gridSize[0]+1):
            pygame.draw.line(screen, BLACK, (i*self.cellSize[0],0), (i*self.cellSize[0],self.gridSize[0]*self.cellSize[1]))
        for j in range(0, self.gridSize[1]+1):
            pygame.draw.line(screen, BLACK, (0,j*self.cellSize[0]) , (self.gridSize[1]*self.cellSize[0],j*self.cellSize[1]))

    # Von Neumann Neighborhood constrained by gridSize
    def get_num_neighbors(self, cell):
        neighbors = 0
        pos = cell.cellpos
        if cell.bomb:
            return -1
        for i in range(-1,2):
            for j in range(-1,2):
                new_x = pos[0] + i
                new_y = pos[1] + j
                if self.gridSize[1] > new_y >= 0 and self.gridSize[0] > new_x >= 0 and pos != (new_x,new_y):
                    if self.cells[new_x,new_y].bomb:
                        neighbors += 1
        return neighbors

    def get_bombs(self):
        colors = [BLACK, BLACK, BLUE, GREEN, RED, PURPLE, ORANGE, PINK, YELLOW, TURQUOISE]
        for cell in self.cells.values():
            cell.bombs = self.get_num_neighbors(cell)
            if cell.bombs == -1:
                cell.text_surface_obj = self.font_obj.render("B", True, BLACK)
            else:
                cell.text_surface_obj = self.font_obj.render(str(cell.bombs), True, colors[cell.bombs+1])
            cell.text_rect_obj = cell.text_surface_obj.get_rect()
            cell.text_rect_obj.center = cell.box.center

    def get_zero_neighborhood(self, cell):
        queue = []
        searched = []
        queue.append(cell)

        while len(queue) > 0:
            curr = queue.pop()
            pos = curr.cellpos
            for i in range(-1,2):
                for j in range(-1,2):
                    new_x = pos[0] + i
                    new_y = pos[1] + j
                    if self.gridSize[1] > new_y >= 0 and self.gridSize[0] > new_x >= 0 and pos != (new_x,new_y):
                        new_cell = self.cells[new_x, new_y]
                        if new_cell.bombs == 0 and new_cell not in searched:
                            queue.append(new_cell)
                        elif new_cell not in searched:
                            searched.append(new_cell)
            searched.append(curr)
        return searched

    def make_visible(self, cell_list):
        for cell in cell_list:
            if not cell.visible:
                self.numNotVisible -= 1
                cell.visible = True

    def draw_bombs(self):
        for cell in self.bombs:
            cell.visible = not cell.visible





def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0

    size = (20, 20)
    sim = Sim(size)

    while True:
        sim.update()
        pygame.display.flip()
        dt = clock.tick(FPS)


if __name__ == '__main__':
    main()
