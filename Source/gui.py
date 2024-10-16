# gui.py

# Graphic User Interface
import os

import random

import pygame


# Path
tile_image_path = os.path.join('..', 'Assets', 'tileset.png')
standard_input_board_path = os.path.join(os.getcwd(), 'input', 'standard')
hard_input_board_path = os.path.join(os.getcwd(), 'input', 'hard')

# Sceen set up (each block is 64 x 64 pixels)
SCREEN_WIDTH = 18 * 64
SCREEN_HEIGHT = 12 * 64
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Tile Set Image
tileset_image = pygame.image.load(tile_image_path).convert_alpha()


# Read an input board file
def get_board(path):
    with open(path, 'r') as file:
        lines = file.readlines()[1:]
        board = [list(line.rstrip('\n')) for line in lines]
    return board

# Return a list of boards
def get_boards(mode_path):
    os.chdir(mode_path)
    list_boards = []
    for file in os.listdir():
        if file.endswith(".txt"):
            file_path = f"{mode_path}\\{file}"
            board = get_board(file_path)
            list_boards.append(board)
    return list_boards


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__() 
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))


def get_tile(tileset, x, y, width=64, height=64, scale_factor=1):
    tile = pygame.Surface((width, height), pygame.SRCALPHA)
    tile.blit(tileset, (0, 0), (x, y, width, height))
    tile = pygame.transform.scale(tile, (width * scale_factor, height * scale_factor))
    return tile

# Render the map for the game
def renderMap(board):
    # Tile Images Init

    ## Walls Images 
    wall_img = get_tile(tileset_image, 448, 448) 
    
    ## White Space Images
    black_space_img = get_tile(tileset_image, 0, 0) # Black Image
    floor_img = get_tile(tileset_image, 704, 384)

    ## Switch Places
    switch_place_img = get_tile(tileset_image, 704, 448)

    ## Stones
    stone_1_img = get_tile(tileset_image, 384, 0)
    stone_2_img = get_tile(tileset_image, 512, 0)
    stone_3_img = get_tile(tileset_image, 576, 0)

    player_img = get_tile(tileset_image, 0, 256) 

    # Get the width and height of the map input and initial the indent's value
    width = len(board[0])
    height = len(board)
    indent_x = (SCREEN_WIDTH - width * 64) / 2.0
    indent_y = (SCREEN_HEIGHT - height * 64) / 2.0

    # Clear the screen first
    screen.fill((0, 0, 0))  

    for i in range(height):
        for j in range(width):
            # Black Spaces that outside the Walls
            if board[i][j] == '%':
                screen.blit(black_space_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Walls
            if board[i][j] == '#':
                screen.blit(wall_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Floors inside the Walls
            if board[i][j] in [' ', '@', '$']:
                screen.blit(floor_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Stones
            if board[i][j] == '$':
                screen.blit(stone_1_img, (j * 64 + indent_x, i * 64 + indent_y))
            
            # Player
            if board[i][j] == '@':
                screen.blit(player_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Switches
            if board[i][j] == '.':
                screen.blit(switch_place_img, (j * 64 + indent_x, i * 64 + indent_y))

def game_loop(board):
    pygame.init()
    pygame.display.set_caption("Ares's Adventure")

    running = True
    while running:
        # Render the board
        renderMap(board)

        pygame.display.update()  # Update the display

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

# Run the command "python gui.py" to run the GUI
maps = get_boards(standard_input_board_path)
game_loop(maps[10])
