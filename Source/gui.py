import os
import pygame
import time
import sys

import utils
from UCS import *
from A_star import *
from BFS import *
from DFS import *

# Font 
pygame.font.init()
font = pygame.font.SysFont(None, 33)

# Path
tile_image_path = os.path.join("Assets/tileset.png")
standard_input_board_path = os.path.join(os.getcwd(),'Source', 'input', 'standard')
hard_input_board_path = os.path.join(os.getcwd(),'Source', 'input', 'hard')

# Sceen set up (each block is 64 x 64 pixels)
SCREEN_WIDTH = 18 * 64
SCREEN_HEIGHT = 12 * 64
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Tile Set Image
tileset_image = pygame.image.load(tile_image_path).convert_alpha()

# Output content
output_content=[]

stop_timeout_event = threading.Event()

def time_limit_check(timeout_duration):
    print('time thread start')
    for _ in range(timeout_duration):
        if stop_timeout_event.is_set():
            print('Timeout thread stopped immediately')
            return  # Thoát ngay khi cờ dừng được bật
        time.sleep(1)
    print('reach timeout')
    utils.timeout_event.set()

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

#Algorithm mode
algorithm_mode="UCS" #UCS is default algorithm

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
PAUSE_BUTTON_POSITION = (200, 50)  
RESET_BUTTON_POSITION = (350, 50)

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
    pygame.draw.rect(screen, (0, 0, 0), (SCREEN_WIDTH - 150, 20, 145, 30))

    status_text = font.render(text, True, (255, 255, 255))
    screen.blit(status_text, (SCREEN_WIDTH - 150, 20))

def render_algorithm_name(name):
    
    pygame.draw.rect(screen, (0, 0, 0), (550, 50, 200, 30))  
    algorithm_text = font.render(name, True, (255, 255, 255))  
    screen.blit(algorithm_text, (550, 70))
    

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

def render_cost_step(current_step, final_cost):

    pygame.draw.rect(screen, (0, 0, 0), (SCREEN_WIDTH - 150, 60, 140, 60))  

    # Render Step count
    step_text = font.render(f"Step: {current_step}", True, (255, 255, 255))
    screen.blit(step_text, (SCREEN_WIDTH - 150, 60))  

    # Render Cost
    current_cost = final_cost[current_step] if current_step < len(final_cost) else 0
    
    cost_text = font.render(f"Cost: {current_cost}", True, (255, 255, 255))
    screen.blit(cost_text, (SCREEN_WIDTH - 150, 100))

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

def flash_rect(text, size, color1, color2, duration=0.5):
    current_time = time.time()
    # Cứ mỗi nửa giây đổi màu giữa color1 và color2
    if int(current_time * 2) % 2 == 0:
        TEXT=get_font(size).render(text,True,color1)
        RECT=TEXT.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    else:
        TEXT=get_font(size).render(text,True,color2)
        RECT=TEXT.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(TEXT,RECT)

def game_loop(board):
    global is_running, is_paused, is_calculating, player_pos, stones, algorithm_mode, output_content, cost_list, final_cost, timeout_reached
    screen.fill("black")
    
    def notify_win():
        global is_running, is_paused, is_calculating, player_pos, stones
        nonlocal move_index
        state=True
        while state:
            WIN_MOUSE_POS=pygame.mouse.get_pos()
            RESTART_BUTTON=Button(image=None,pos=(SCREEN_WIDTH//2-120,SCREEN_HEIGHT//2+70)
                            ,text_input="RESTART",font=get_font(30),base_color="White",hovering_color="Green")
            MENU_BUTTON=Button(image=None,pos=(SCREEN_WIDTH//2+120,SCREEN_HEIGHT//2+70)
                            ,text_input="MENU",font=get_font(30),base_color="White",hovering_color="Green")
            for button in [RESTART_BUTTON,MENU_BUTTON]:
                button.changeColor(WIN_MOUSE_POS)
                button.update(screen)
        
            flash_rect('YOU WIN!',60,'White','Yellow')
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if RESTART_BUTTON.checkForInput(WIN_MOUSE_POS):
                        move_index = 0
                        player_pos = initial_state['player_pos'].copy()
                        stones = initial_state['stones'].copy()
                        is_paused = True
                        render_map(board)
                        render_buttons()
                        state=False
                    if MENU_BUTTON.checkForInput(WIN_MOUSE_POS):
                        main_menu()
            pygame.display.update()
    
    def notify_timeout():
        global is_running, is_paused, is_calculating, player_pos, stones
        nonlocal move_index
        state=True
        while state:
            WIN_MOUSE_POS=pygame.mouse.get_pos()
            MENU_BUTTON=Button(image=None,pos=(SCREEN_WIDTH//2+120,SCREEN_HEIGHT//2+70)
                            ,text_input="MENU",font=get_font(30),base_color="White",hovering_color="Green")
            
            MENU_BUTTON.changeColor(WIN_MOUSE_POS)
            MENU_BUTTON.update(screen)
        
            flash_rect('TIMEOUT!',60,'White','Yellow')
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if MENU_BUTTON.checkForInput(WIN_MOUSE_POS):
                        main_menu()
            pygame.display.update()
            
    # Reset để chạy map
    player_pos=[0,0]
    stones.clear()
    switches_pos.clear()
    cost_list = [0]
    graph_way_nodes.clear()
    
    render_map(board) 
    render_buttons()
    render_algorithm_name(utils.algorithm_mode)
    pygame.display.update()

    # Show "Calculating" while starting calculations
    is_calculating = True 
    calculation_thread = threading.Thread(target=calculation_animation)
    calculation_thread.start()
    
    #Set timeout thread
    utils.timeout_reached = False
    timeout_duration = 20  # 1 minutes
    timeout_thread = threading.Thread(target=time_limit_check, args=(timeout_duration,))
    timeout_thread.start()

    # Initialize state
    initial_state = {
        'player_pos': player_pos.copy(),
        'stones': stones.copy()
    }
    
    # Run algorithm
    problem = utils.Problem(initial_state, board, switches_pos, graph_way_nodes)

    output_content.clear()
    ucs_go=ucs(problem, output_content)
    bfs_go=bfs(problem, output_content)
    dfs_go=dfs(problem, output_content)
    a_star_go=a_star(problem, output_content)
    print("finish")
    
    for i in [ucs_go, bfs_go, dfs_go, a_star_go]:
        if i is None and utils.timeout_event.is_set():
            timeout_thread.join()
            is_calculating = False  
            utils.timeout_event.clear()
            calculation_thread.join()
            notify_timeout()
    
    stop_timeout_event.set()
    timeout_thread.join()
    stop_timeout_event.clear()
    save_output_to_file(current_map_path, output_content)
    
    if utils.algorithm_mode=='UCS':
        way_player_go=ucs_go
    elif utils.algorithm_mode=='BFS':
        way_player_go=bfs_go
    elif utils.algorithm_mode=='DFS':
        way_player_go=dfs_go
    elif utils.algorithm_mode=='A*':
        way_player_go=a_star_go

    is_calculating = False  
    calculation_thread.join() 
    
    # Delete calculating
    pygame.draw.rect(screen, (0, 0, 0), (SCREEN_WIDTH - 150, 20, 145, 30))  

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
                    render_algorithm_name(utils.algorithm_mode)
                    pygame.display.update()

        if is_win():
            notify_win()
        if not is_paused and move_index < len(way_player_go):
            movement(board, way_player_go[move_index])
            
            move_index += 1

        if not way_player_go:
            text = font.render("THERE IS NO WAY TO WIN!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

        if is_calculating:
            render_status_text("Calculating")
        else:
            render_status_text("Finish")

        render_buttons()
        render_cost_step(move_index, utils.final_cost)
        pygame.display.update()

    pygame.quit()

current_map_directory=standard_input_board_path #default is standard
current_map_path='input-01.txt' #input01 is default input
map=get_board(os.path.join(current_map_directory,current_map_path))
#Create MENU
class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

BG = pygame.image.load("Assets/Background.png")
def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("Assets/font.ttf", size)

def getFilesName(mapDirectory):
    mapArr=[]
    for file_name in os.listdir(mapDirectory):
        if file_name.endswith('.txt'):
            mapArr.append(file_name)
    return mapArr

def map_choose():
    global map, current_map_path
    while True:
        screen.fill("black")
        screen.blit(BG,(0,0))
        MAP_MOUSE_POS=pygame.mouse.get_pos()
        
        MAP_TEXT=get_font(60).render("CHOOSE MAP",True,"White")
        MAP_RECT=MAP_TEXT.get_rect(center=(SCREEN_WIDTH//2,100))
        screen.blit(MAP_TEXT,MAP_RECT)

        mapArr = getFilesName(current_map_directory)

        x_position=255
        y_position=255
        y_gap=30
        x_gap=200
        map_button_list=[]

        for index, mapName in enumerate(mapArr):
            mapText = f"MAP{index+1:02d}"
            MAP_NAME_BUTTON=Button(image=None,pos=(x_position,y_position)
                    ,text_input=mapText,font=get_font(20),base_color="White",hovering_color="Green")
            map_button_list.append(MAP_NAME_BUTTON)
            if (index+1)%15==0:
                x_position+=x_gap
                y_position=255
                continue
            y_position+=y_gap

        for button in map_button_list:
            button.changeColor(MAP_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                for index, button in enumerate(map_button_list):
                    if button.checkForInput(MAP_MOUSE_POS):
                        current_map_path=mapArr[index]
                        map=get_board(os.path.join(current_map_directory, current_map_path))
                        main_menu()

        pygame.display.update()

def mode_choose():
    global current_map_directory, current_map_path, map
    while True:
        screen.fill("black")
        screen.blit(BG,(0,0))
        MODE_MOUSE_POS=pygame.mouse.get_pos()
        
        MODE_TEXT=get_font(60).render("CHOOSE MODE",True,"White")
        MODE_RECT=MODE_TEXT.get_rect(center=(SCREEN_WIDTH//2,100))
        screen.blit(MODE_TEXT,MODE_RECT)

        STANDARD_BUTTON=Button(image=pygame.image.load('Assets/LongRect.png'),pos=(SCREEN_WIDTH//2, 325)
                                ,text_input='STANDARD',font=get_font(50),base_color="White",hovering_color="Green")
        HARD_BUTTON=Button(image=pygame.image.load('Assets/LongRect.png'),pos=(SCREEN_WIDTH//2, 475)
                            ,text_input='HARD',font=get_font(50),base_color="White",hovering_color="Green")
        for button in [STANDARD_BUTTON,HARD_BUTTON]:
            button.changeColor(MODE_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if STANDARD_BUTTON.checkForInput(MODE_MOUSE_POS):
                    current_map_directory=standard_input_board_path
                    current_map_path="input-01.txt"
                    map=get_board(os.path.join(current_map_directory,current_map_path))
                if HARD_BUTTON.checkForInput(MODE_MOUSE_POS):
                    current_map_directory=hard_input_board_path
                    current_map_path="input-06.txt"
                    map=get_board(os.path.join(current_map_directory,current_map_path))
                main_menu()

        pygame.display.update()

def algorithm_choose():
    global algorithm_mode
    while True:
        screen.fill("black")
        screen.blit(BG,(0,0))
        ALGORITHM_MOUSE_POS=pygame.mouse.get_pos()

        ALGORITHM_TEXT=get_font(60).render("CHOOSE ALGORITHM",True,"White")
        ALGORITHM_RECT=ALGORITHM_TEXT.get_rect(center=(SCREEN_WIDTH//2,100))
        screen.blit(ALGORITHM_TEXT,ALGORITHM_RECT)

        UCS_BUTTON = Button(image=pygame.image.load("Assets/Rect.png"), pos=(SCREEN_WIDTH//2, 225), 
                            text_input="UCS", font=get_font(50), base_color="White", hovering_color="Green")
        BFS_BUTTON = Button(image=pygame.image.load("Assets/Rect.png"),pos=(SCREEN_WIDTH//2, 350), 
                            text_input="BFS", font=get_font(50), base_color="White", hovering_color="Green")
        DFS_BUTTON=Button(image=pygame.image.load("Assets/Rect.png"), pos=(SCREEN_WIDTH//2, 475), 
                            text_input="DFS", font=get_font(50), base_color="White", hovering_color="Green")
        A_STAR_BUTTON = Button(image=pygame.image.load("Assets/Rect.png"), pos=(SCREEN_WIDTH//2, 600), 
                            text_input="A*", font=get_font(50), base_color="White", hovering_color="Green")
        
        for button in [UCS_BUTTON,BFS_BUTTON,DFS_BUTTON,A_STAR_BUTTON]:
            button.changeColor(ALGORITHM_MOUSE_POS)
            button.update(screen)
        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if UCS_BUTTON.checkForInput(ALGORITHM_MOUSE_POS):
                    utils.algorithm_mode="UCS"
                if BFS_BUTTON.checkForInput(ALGORITHM_MOUSE_POS):
                    utils.algorithm_mode="BFS"
                if DFS_BUTTON.checkForInput(ALGORITHM_MOUSE_POS):
                    utils.algorithm_mode="DFS"
                if A_STAR_BUTTON.checkForInput(ALGORITHM_MOUSE_POS):
                    utils.algorithm_mode="A*"
                main_menu()

        pygame.display.update()

def main_menu():
    global map, current_map_path
    while True:
        screen.blit(BG,(0,0))
        MENU_MOUSE_POS=pygame.mouse.get_pos()
        
        MENU_TEXT = get_font(60).render("Ares's Adventure",True,"#b68f40")
        MENU_RECT=MENU_TEXT.get_rect(center=(SCREEN_WIDTH//2,100))
        PLAY_BUTTON = Button(image=pygame.image.load("Assets/Rect.png"), pos=(SCREEN_WIDTH//2, 220), 
                            text_input="PLAY", font=get_font(50), base_color="White", hovering_color="Green")
        MAP_BUTTON = Button(image=pygame.image.load("Assets/Rect.png"),pos=(SCREEN_WIDTH//2, 330), 
                            text_input="MAP", font=get_font(50), base_color="White", hovering_color="Green")
        MODE_BUTTON=Button(image=pygame.image.load("Assets/Rect.png"), pos=(SCREEN_WIDTH//2, 440), 
                            text_input="MODE", font=get_font(50), base_color="White", hovering_color="Green")
        ALGORITHM_BUTTON=Button(image=pygame.image.load("Assets/LongRect.png"), pos=(SCREEN_WIDTH//2, 550), 
                            text_input="AlGORITHM", font=get_font(50), base_color="White", hovering_color="Green")
        QUIT_BUTTON = Button(image=pygame.image.load("Assets/Rect.png"), pos=(SCREEN_WIDTH//2, 660), 
                            text_input="QUIT", font=get_font(50), base_color="White", hovering_color="Green")
        screen.blit(MENU_TEXT,MENU_RECT)

        for button in [PLAY_BUTTON,MAP_BUTTON,MODE_BUTTON,ALGORITHM_BUTTON,QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    game_loop(map)
                if MAP_BUTTON.checkForInput(MENU_MOUSE_POS):
                    map_choose()
                if MODE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mode_choose()
                if ALGORITHM_BUTTON.checkForInput(MENU_MOUSE_POS):
                    algorithm_choose()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.update()