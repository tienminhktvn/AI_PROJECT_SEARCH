import os
import pygame
import threading
import time

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
hard_input_board_path = os.path.join(os.getcwd(), 'input', 'standard')

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

# Status
is_running = False
is_paused = False
is_calculating = True

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
    screen.fill((0, 0, 0)) 
    width = len(board[0])
    height = len(board)

    weight_index = 0 

    for i in range(height):
        for j in range(width):
            # Use the add_connection function to point out which action player can move at a particular position
            if board[i][j] not in ['%', '#']:
                add_connection(board, graph_way_nodes, (j, i), (j-1, i), (j, i-1), (j+1, i), (j, i+1))

            # Black Spaces that are outside the Walls
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
                if weight_index < len(weights):
                    stones[(j, i)] = weights[weight_index]  
                    weight_index += 1  
                render_stones(board)
                
            # Player
            if board[i][j] == '@':
                player_pos[0] = j
                player_pos[1] = i
                render_player(board)

            # Switches
            if board[i][j] == '.':
                screen.blit(switch_place_img, (j * 64 + indent_x, i * 64 + indent_y))
                switches_pos.append((j, i))




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
        delay_time = 300
    else:
        delay_time = 700
    
    pygame.time.wait(delay_time)

# Render switches
def render_switches(board,old_pos_player):
    indent_x, indent_y = get_IndentX_IndentY(board)
    if(tuple(old_pos_player) in switches_pos):
        screen.blit(switch_place_img, (old_pos_player[0] * 64 + indent_x, old_pos_player[1] * 64 + indent_y))
        
        
        
# Button size
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50

# Button position
START_BUTTON_POSITION = (50, 50)  
PAUSE_BUTTON_POSITION = (50, 110) 
RESET_BUTTON_POSITION = (50, 170) 

def render_buttons():

    pygame.draw.rect(screen, (0, 255, 0), (START_BUTTON_POSITION[0], START_BUTTON_POSITION[1], BUTTON_WIDTH, BUTTON_HEIGHT))
    start_text = font.render("Start", True, (0, 0, 0))
    screen.blit(start_text, (START_BUTTON_POSITION[0] + 10, START_BUTTON_POSITION[1] + 10))


    pygame.draw.rect(screen, (255, 255, 0), (PAUSE_BUTTON_POSITION[0], PAUSE_BUTTON_POSITION[1], BUTTON_WIDTH, BUTTON_HEIGHT))
    pause_text = font.render("Pause", True, (0, 0, 0))
    screen.blit(pause_text, (PAUSE_BUTTON_POSITION[0] + 10, PAUSE_BUTTON_POSITION[1] + 10))


    pygame.draw.rect(screen, (255, 0, 0), (RESET_BUTTON_POSITION[0], RESET_BUTTON_POSITION[1], BUTTON_WIDTH, BUTTON_HEIGHT))
    reset_text = font.render("Reset", True, (0, 0, 0))
    screen.blit(reset_text, (RESET_BUTTON_POSITION[0] + 10, RESET_BUTTON_POSITION[1] + 10))
    
def render_status_text(text):
    """Hàm hiển thị dòng trạng thái ở góc màn hình."""
    status_text = font.render(text, True, (255, 255, 255))  
    screen.blit(status_text, (SCREEN_WIDTH - 150, 20)) 
    
def calculation_animation():
    global is_calculating
    dot_count = 0
    max_dots = 3 

    while is_calculating:
        # Create the loading text with dots
        loading_text = "Calculating" + "." * dot_count
        render_status_text(loading_text)  # Function to render text on the screen
        pygame.display.update()
        
        dot_count = (dot_count + 1) % (max_dots + 1) 
        time.sleep(0.5) 


def movement(board, node):
    x = 0
    y = 1
    player_move = 0  # move left: 1, move up: 2, move right: 3, move down: 4
    indent_x, indent_y = get_IndentX_IndentY(board)
    delay_time = 500  # Delay time between each move

    old_pos_player = player_pos.copy()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return

    pygame.time.delay(delay_time)

    if (player_pos[x] - node[x] == 1):
        player_pos[x] -= 1
        player_move = 1
    elif (player_pos[y] - node[y] == 1):
        player_pos[y] -= 1
        player_move = 2
    elif (player_pos[x] - node[x] == -1):
        player_pos[x] += 1
        player_move = 3
    elif (player_pos[y] - node[y] == -1):
        player_pos[y] += 1
        player_move = 4

    if node in stones:
        movement_delay(stones[node])

        old_pos_stone = node
        if player_move == 1:
            new_pos_stone = (node[x] - 1, node[y]) 
        elif player_move == 2:
            new_pos_stone = (node[x], node[y] - 1)  
        elif player_move == 3:
            new_pos_stone = (node[x] + 1, node[y])  
        elif player_move == 4:
            new_pos_stone = (node[x], node[y] + 1) 

        stones[new_pos_stone] = stones.pop(old_pos_stone)
        screen.blit(floor_img, (old_pos_stone[0] * 64 + indent_x, old_pos_stone[1] * 64 + indent_y))  
        render_stones(board)  

    screen.blit(floor_img, (old_pos_player[0] * 64 + indent_x, old_pos_player[1] * 64 + indent_y))  
    render_switches(board, old_pos_player) 
    render_player(board)  
    pygame.display.update()  


def is_win():
    for stone in stones:
        if stone not in switches_pos:
            return False
    
    return True

def game_loop(board):
    global is_running, is_paused, is_calculating, player_pos, stones

    pygame.init()
    pygame.display.set_caption("Ares's Adventure")

    render_map(board)  
    render_buttons()
    pygame.display.update()

    # Show "Calculating" while starting calculations
    is_calculating = True 
    calculation_thread = threading.Thread(target=calculation_animation)
    calculation_thread.start()

    # Initialize state
    initial_state = {
        'player_pos': player_pos.copy(),
        'stones': stones.copy()
    }

    # Run A* algorithm
    problem = utils.Problem(initial_state, board, switches_pos, graph_way_nodes)
    way_player_go = a_star(problem)

    is_calculating = False  
    calculation_thread.join() 
    
    # Delete calculating
    pygame.draw.rect(screen, (0, 0, 0), (SCREEN_WIDTH - 150, 20, 145, 30))  # Xóa dòng "Calculating"

    # Update text to "Finish"
    render_status_text("Finish")
    pygame.display.update()

    # Game control variables
    move_index = 0
    is_running = True
    is_paused = True

    # Main game loop
    while is_running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if START_BUTTON_POSITION[0] <= mouse_pos[0] <= START_BUTTON_POSITION[0] + BUTTON_WIDTH and \
                    START_BUTTON_POSITION[1] <= mouse_pos[1] <= START_BUTTON_POSITION[1] + BUTTON_HEIGHT:
                    is_paused = False
                elif PAUSE_BUTTON_POSITION[0] <= mouse_pos[0] <= PAUSE_BUTTON_POSITION[0] + BUTTON_WIDTH and \
                    PAUSE_BUTTON_POSITION[1] <= mouse_pos[1] <= PAUSE_BUTTON_POSITION[1] + BUTTON_HEIGHT:
                    is_paused = True
                elif RESET_BUTTON_POSITION[0] <= mouse_pos[0] <= RESET_BUTTON_POSITION[0] + BUTTON_WIDTH and \
                    RESET_BUTTON_POSITION[1] <= mouse_pos[1] <= RESET_BUTTON_POSITION[1] + BUTTON_HEIGHT:
                    move_index = 0
                    player_pos = initial_state['player_pos'].copy()
                    stones = initial_state['stones'].copy()
                    is_paused = True
                    render_map(board)
                    render_buttons()
                    pygame.display.update()

        if is_win():
            text = font.render("YOU WIN!", True, (0, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

        if not is_paused and move_index < len(way_player_go):
            movement(board, way_player_go[move_index])
            move_index += 1

        if not way_player_go:
            text = font.render("THERE IS NO WAY TO WIN!", True, (0, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

        if is_calculating:
            render_status_text("Calculating")
        else:
            render_status_text("Finish")

        render_buttons()
        pygame.display.update()

    pygame.quit()




# Run the command "python gui.py" to run the GUI
map = get_board(os.path.join(standard_input_board_path, 'input01.txt'))
game_loop(map)

