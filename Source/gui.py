import os
import time
import pygame

import utils
from UCS import *
from A_star import *
from BFS import *
from DFS import *

# Font 
pygame.font.init()
font = pygame.font.SysFont(None, 33)

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
    global weights
    with open(path, 'r') as file:
        weight_line = file.readline().strip().split(' ')
        map_lines = file.readlines()[0:]
        weights = [int(weight) for weight in weight_line]
        board = [list(line.rstrip('\n')) for line in map_lines]
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

def get_tile(tileset, x, y, width=64, height=64, scale_factor=1):
    tile = pygame.Surface((width, height), pygame.SRCALPHA)
    tile.blit(tileset, (0, 0), (x, y, width, height))
    tile = pygame.transform.scale(tile, (width * scale_factor, height * scale_factor))
    return tile

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

## Player
player_img = get_tile(tileset_image, 0, 256) 

# Player Position
player_pos = [0, 0]

# Stones has position and weight
stones = {}

# Weights of stones
weights = []

# Graph 
graph_way_nodes = {} # conatain nodes 

# Switches Position
switches_pos = []


def get_IndentX_IndentY(board):
    # Get the width and height of the map input
    width = len(board[0])
    height = len(board)
    indent_x = (SCREEN_WIDTH - width * 64) / 2.0
    indent_y = (SCREEN_HEIGHT - height * 64) / 2.0

    return indent_x, indent_y


# Function to add a connection between nodes in graph
def add_connection(board, graph, node, left_pos, up_pos, right_pos, down_pos):
    if node not in graph:
        graph[node] = []
    
    if (left_pos[0] >= 0):
        if (board[left_pos[1]][left_pos[0]] != '#'):
            graph[node].append(left_pos)

    if (up_pos[1] >= 0):
        if (board[up_pos[1]][up_pos[0]] != '#'):
            graph[node].append(up_pos)
    if (right_pos[0] < len(board[0])):
        if (board[right_pos[1]][right_pos[0]] != '#'):
            graph[node].append(right_pos)

    if (down_pos[1] < len(board)):
        if (board[down_pos[1]][down_pos[0]] != '#'):
            graph[node].append(down_pos)


# Render the map for the game
def render_map(board):
    indent_x, indent_y = get_IndentX_IndentY(board)
    screen.fill((0, 0, 0)) # Clear the screen first (e.g., with a black background)
    width = len(board[0])
    height = len(board)

    for i in range(height):
        for j in range(width):
            # Use the add_connection function to point out which action player can move at a particular position
            if board[i][j] not in ['%', '#']:
                add_connection(board, graph_way_nodes, (j, i), (j-1, i), (j, i-1), (j+1, i), (j, i+1))

            # Black Spaces that outside the Walls
            if board[i][j] == '%':
                screen.blit(black_space_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Walls
            if board[i][j] == '#':
                screen.blit(wall_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Floor
            if board[i][j] in [' ', '@', '$']:
                screen.blit(floor_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Stones
            if board[i][j] == '$':
                stones[(j, i)] = weights.pop(0)
                render_stones(board)

            # Switches
            if board[i][j] in ['.', '+']:
                screen.blit(switch_place_img, (j * 64 + indent_x, i * 64 + indent_y))
                switches_pos.append((j, i))

            # Player
            if board[i][j] in ['@', '+']:
                player_pos[0] = j
                player_pos[1] = i
                render_player(board)


# Render player
def render_player(board):
    indent_x, indent_y = get_IndentX_IndentY(board)
    screen.blit(player_img, (player_pos[0] * 64 + indent_x, player_pos[1] * 64 + indent_y))


# Render stones
def render_stones(board):
    indent_x, indent_y = get_IndentX_IndentY(board)
    for stone in stones:
        stone_x = stone[0] * 64 + indent_x
        stone_y = stone[1] * 64 + indent_y

        # Get the weight of the stone to draw it upon the image
        weight = stones[stone]

        if weight > 0 and weight < 30:
            stone_img = stone_1_img
        elif weight < 70:
            stone_img = stone_2_img
        else:
            stone_img = stone_3_img

        screen.blit(stone_img, (stone_x, stone_y))

        stone_rect = pygame.Rect(stone_x, stone_y, 64, 64)  

        # Draw circle upon the stone
        pygame.draw.circle(screen, (0, 0, 0), stone_rect.center, 25) 
        pygame.draw.circle(screen, (255, 255, 255), stone_rect.center, 23) 

        text = font.render(str(weight), True, (0,0,0))
        text_rect = text.get_rect(center=stone_rect.center)
        screen.blit(text, text_rect)


# Delay the move based on the weight of the stones
def movement_delay(weight):
    if weight > 0 and weight < 30:
        delay_time = 0
    elif weight < 70:
        delay_time = 0.3
    else:
        delay_time = 0.7
    
    time.sleep(delay_time)

# Render switches
def render_switches(board,old_pos_player):
    indent_x, indent_y = get_IndentX_IndentY(board)
    if(tuple(old_pos_player) in switches_pos):
        screen.blit(switch_place_img, (old_pos_player[0] * 64 + indent_x, old_pos_player[1] * 64 + indent_y))

def movement(board, way):
    x = 0
    y = 1
    player_move = 0 # move left: 1, move up: 2, move right: 3, move down: 4
    indent_x, indent_y = get_IndentX_IndentY(board)
    delay_time = 500 # Delay time between each move

    for node in way:
        pygame.time.delay(delay_time)  # Delay time between each move
        old_pos_player = player_pos.copy()

        if (player_pos[x] - node[x] == 1):
            # Move left
            player_pos[x] -= 1
            player_move = 1
        elif (player_pos[y] - node[y] == 1):
            # Move up
            player_pos[y] -= 1
            player_move = 2
        elif (player_pos[x] - node[x] == -1):
            # Move right
            player_pos[x] += 1
            player_move = 3
        elif (player_pos[y] - node[y] == -1):
            # Move down
            player_pos[y] += 1
            player_move = 4

        if(node in stones):
            # Delay the movement based on the weight of the stone
            movement_delay(stones[node])

            old_pos_stone = node
            if (player_move == 1):
                # Move left
                new_pos_stone = (node[x] - 1, node[y])
                stones[new_pos_stone] = stones.pop(old_pos_stone)
            elif (player_move == 2):
                # Move up
                new_pos_stone = (node[x], node[y] - 1)
                stones[new_pos_stone] = stones.pop(old_pos_stone)
            elif (player_move == 3):
                # Move right
                new_pos_stone = (node[x] + 1, node[y])
                stones[new_pos_stone] = stones.pop(old_pos_stone)
            elif (player_move == 4):
                # Move down
                new_pos_stone = (node[x], node[y] + 1)
                stones[new_pos_stone] = stones.pop(old_pos_stone)

            screen.blit(floor_img, (old_pos_stone[0] * 64 + indent_x, old_pos_stone[1] * 64 + indent_y)) # Clear old stone position
            render_stones(board) # Draw stone at new position
        
        screen.blit(floor_img, (old_pos_player[0] * 64 + indent_x, old_pos_player[1] * 64 + indent_y)) # Clear old player position
        render_switches(board, old_pos_player) # Draw switch at new player position if exist
        render_player(board) # Draw player at new position  
        pygame.display.update()  # Update the display


# Return True = Win, False = Not Win Yet
def is_win():
    for stone in stones:
        if stone not in switches_pos:
            return False
    
    return True

def game_loop(board):
    pygame.init()
    pygame.display.set_caption("Ares's Adventure")

    render_map(board) # Create the map for first time
    pygame.display.update()  # Update the display

    # Create the problem instance
    initial_state = {
        'player_pos': player_pos,
        'stones': stones
    }

    problem = utils.Problem(initial_state, board, switches_pos, graph_way_nodes)

    # Use algorithm
    start = time.time()
    way_player_go = ucs(problem)
    end = time.time()
    elapsed = end - start
    print(f'Time taken: {elapsed:.6f} seconds')
    # print(way_player_go)

    if way_player_go:
        movement(board, way_player_go) # Move the player
    else:
        text = font.render("THERE NO NO WAY TO WIN!", True, (0, 0, 0))  # Render the text
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))  # Center the text
        screen.blit(text, text_rect)  # Draw the text on the screen

    running = True
    while running:
        pygame.display.update()  # Update the display

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        ## Test for winning ##
            if is_win():
                text = font.render("YOU WIN!", True, (0, 0, 0))  # Render the text
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))  # Center the text
                screen.blit(text, text_rect)  # Draw the text on the screen
        
    pygame.quit()


# Run the command "python gui.py" to run the GUI
map = get_board(os.path.join(standard_input_board_path, 'input17.txt'))
game_loop(map)
