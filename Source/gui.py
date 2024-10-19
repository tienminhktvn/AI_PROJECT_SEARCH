import os
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
graph_way_nodes = {} #conatain nodes 


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
    if (board[left_pos[0]][left_pos[1]] != '#'):
        graph[node].append(left_pos)
    if (board[up_pos[0]][up_pos[1]] != '#'):
        graph[node].append(up_pos)
    if (board[right_pos[0]][right_pos[1]] != '#'):
        graph[node].append(right_pos)
    if (board[down_pos[0]][down_pos[1]] != '#'):
        graph[node].append( down_pos)


# Render the map for the game
def render_map(board):
    indent_x, indent_y = get_IndentX_IndentY(board)
    screen.fill((0, 0, 0)) # Clear the screen first (e.g., with a black background)
    width = len(board[0])
    height = len(board)

    for i in range(height):
        for j in range(width):
            # Black Spaces that outside the Walls
            if board[i][j] == '%':
                screen.blit(black_space_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Walls
            if board[i][j] == '#':
                screen.blit(wall_img, (j * 64 + indent_x, i * 64 + indent_y))

            # Floor
            if board[i][j] in [' ', '@', '$']:
                screen.blit(floor_img, (j * 64 + indent_x, i * 64 + indent_y))
                add_connection(board, graph_way_nodes, (i, j), (i, j-1), (i-1, j), (i, j+1), (i+1, j))

            # Stones
            if board[i][j] == '$':
                stones[(j, i)] = weights.pop(0)
                render_stones(board)
                
            # Player
            if board[i][j] == '@':
                player_pos[0] = j
                player_pos[1] = i
                render_player(board)

            # Switches
            if board[i][j] == '.':
                screen.blit(switch_place_img, (j * 64 + indent_x, i * 64 + indent_y))


# Render player
def render_player(board):
    indent_x, indent_y = get_IndentX_IndentY(board)
    screen.blit(player_img, (player_pos[0] * 64 + indent_x, player_pos[1] * 64 + indent_y))


# Render stones
def render_stones(board):
    indent_x, indent_y = get_IndentX_IndentY(board)
    for stone in stones:
        screen.blit(stone_1_img, (stone[0] * 64 + indent_x, stone[1] * 64 + indent_y))    


def movement(board, way):
    x = 0
    y = 1
    player_move = 0 # move left: 1, move up: 2, move right: 3, move down: 4
    indent_x, indent_y = get_IndentX_IndentY(board)
    delay_time = 1000 # Delay time between each move

    for node in way:
        pygame.time.delay(delay_time)  # Delay time between each move
        old_pos_player = player_pos.copy()

        if (player_pos[x] - node[x] == 1):
            #Move left
            player_pos[x] -= 1
            player_move = 1
        elif (player_pos[y] - node[y] == 1):
            #Move up
            player_pos[y] -= 1
            player_move = 2
        elif (player_pos[x] - node[x] == -1):
            #Move right
            player_pos[x] += 1
            player_move = 3
        elif (player_pos[y] - node[y] == -1):
            #Move down
            player_pos[y] += 1
            player_move = 4

        if(node in stones):
            old_pos_stone = node
            if (player_move == 1):
                #Move left
                new_pos_stone = (node[x] - 1, node[y])
                stones[new_pos_stone] = stones.pop(old_pos_stone)
            elif (player_move == 2):
                #Move up
                new_pos_stone = (node[x], node[y] - 1)
                stones[new_pos_stone] = stones.pop(old_pos_stone)
            elif (player_move == 3):
                #Move right
                new_pos_stone = (node[x] + 1, node[y])
                stones[new_pos_stone] = stones.pop(old_pos_stone)
            elif (player_move == 4):
                #Move down
                new_pos_stone = (node[x], node[y] + 1)
                stones[new_pos_stone] = stones.pop(old_pos_stone)
            screen.blit(floor_img, (old_pos_stone[0] * 64 + indent_x, old_pos_stone[1] * 64 + indent_y)) # Clear old stone position
            render_stones(board) # Draw stone at new position
        
        screen.blit(floor_img, (old_pos_player[0] * 64 + indent_x, old_pos_player[1] * 64 + indent_y)) # Clear old player position
        render_player(board) # Draw player at new position  
        pygame.display.update()  # Update the display
        

def game_loop(board):
    pygame.init()
    pygame.display.set_caption("Ares's Adventure")

    render_map(board) #Create the map for first time
    pygame.display.update()  # Update the display
    movement(board, way_player_go) #Move the player

    running = True

    while running:
        pygame.display.update()  # Update the display

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
    pygame.quit()


# The first element of 'way_player_go' contains the next position player will go, not current position of player
# (5,4) => horizontal is 5, Vertical is 4
way_player_go =[(5, 2), (5, 1), (6,1), (6, 2), (5, 2), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3)  ]

# Run the command "python gui.py" to run the GUI
map =get_board(os.path.join(standard_input_board_path, 'input01.txt'))
game_loop(map)
