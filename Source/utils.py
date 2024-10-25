import os
import time
import tracemalloc
import heapq

"""
A state or initial_state is a dict of player_pos, stone's positions. For example:
    initial_state = {
        'player_pos': [3,3],
        'stones': {
            (3,2): 2,
            (3,4): 50,
            (2,6): 100
        }
    }
"""


class Node:
    def __init__(self, state, parent=None, action=None, cost=0, heuristic=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost                        # g(n)
        self.heuristic = heuristic              # Heuristic h(n)
        self.f = self.cost + self.heuristic     # f(n) = g(n) + h(n)
        self.depth = depth
        
    
    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    # Allow the Node object to be used as a key in a dict
    def __hash__(self):
        return hash((
            tuple(self.state['player_pos']),
            frozenset(self.state['stones'].items())
        ))

# Caculate the Mahhattan distance between two postition
def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class Problem:
    def __init__(self, initial_state, board, switches_pos, graph_way_nodes):
        self.initial_state = initial_state          
        self.board = board 
        self.switches_pos = switches_pos
        self.graph_way_nodes = graph_way_nodes 

    # The player was in the goal if all all stones are in the switches position
    def goal_test(self, state):
        stones = state['stones']
        return all(stone in self.switches_pos for stone in stones)


    def actions(self, state):
        player_pos, stones = state['player_pos'], state['stones']
        actions = self.graph_way_nodes[tuple(player_pos)]

        valid_actions = [] 

        # Check if the player pushes the stone out of the wall
        for action in actions:
            new_stone_positions = stones.copy()
            is_valid = True

            for stone_pos in new_stone_positions:
                if tuple(action) == stone_pos:    
                    new_stone_pos = list(stone_pos)

                    # Push up
                    if player_pos[0] == stone_pos[0] and player_pos[1] > stone_pos[1]:
                        new_stone_pos[1] -= 1

                    # Push down
                    elif player_pos[0] == stone_pos[0] and player_pos[1] < stone_pos[1]:
                        new_stone_pos[1] += 1

                    # Push left
                    elif player_pos[0] > stone_pos[0] and player_pos[1] == stone_pos[1]:
                        new_stone_pos[0] -= 1

                    # Push right
                    elif player_pos[0] < stone_pos[0] and player_pos[1] == stone_pos[1]:
                        new_stone_pos[0] += 1

                    if self.board[new_stone_pos[1]][new_stone_pos[0]] == '#' or (tuple(new_stone_pos) in stones):
                        is_valid = False
                        break

            if is_valid:
                valid_actions.append(action)

        return valid_actions
    

    def heuristic(self, state):
        stones = list(state['stones'].keys())
        total_distance = 0
        assigned_switches = []

        for stone in stones:
            min_distance = float('inf')
            closest_switch = None

            # Find the closet switch for the stone
            for switch in self.switches_pos:
                if switch not in assigned_switches:
                    distance = manhattan_distance(stone, switch) * state['stones'][stone]             

                    if distance < min_distance:
                        min_distance = distance
                        closest_switch = switch

            assigned_switches.append(closest_switch)
            total_distance += min_distance 

        return total_distance


def child_node(problem, node, action, use_heuristic=False):
    # g(n) cost default is 1, if push the stone then cost = weight of stone
    cost = 1

    player_pos, stones = node.state['player_pos'], node.state['stones']
    new_stone_positions = stones.copy()
    
    if not use_heuristic:
        heuristic = 0
    else:
        heuristic = problem.heuristic(node.state)

    # Check if push the stone or not
    for stone in stones:
        if tuple(action) == stone:
            cost = stones[stone] 
            new_stone_pos = list(stone)

            # Push up
            if player_pos[0] == stone[0] and player_pos[1] > stone[1]:
                new_stone_pos[1] -= 1

            # Push down
            elif player_pos[0] == stone[0] and player_pos[1] < stone[1]:
                new_stone_pos[1] += 1

            # Push left
            elif player_pos[0] > stone[0] and player_pos[1] == stone[1]:
                new_stone_pos[0] -= 1

            # Push right
            elif player_pos[0] < stone[0] and player_pos[1] == stone[1]:
                new_stone_pos[0] += 1
            
            # Update the stone's position of the child
            del new_stone_positions[stone]                    # Remove old position
            new_stone_positions[tuple(new_stone_pos)] = cost  # Add new position
    

    child_state = {
        'player_pos': action,
        'stones': new_stone_positions
    }

    return Node(child_state, node, action, cost + node.cost, heuristic)


def solution(node):
    path = []
    while node.parent is not None:
        path.append(node.action)
        node = node.parent
    path.reverse()
    return path

# Add movement actions to output
def generate_action_string(path, problem):
    action_string = []
    state = problem.initial_state

    for action in path:
        player_pos, stones = state['player_pos'], state['stones']

        # Determine if it's a movement or a push action
        if tuple(action) in stones:
            stone_pos = action
            if player_pos[0] == stone_pos[0] and player_pos[1] > stone_pos[1]:
                action_string.append('U')
            elif player_pos[0] == stone_pos[0] and player_pos[1] < stone_pos[1]:
                action_string.append('D')
            elif player_pos[0] > stone_pos[0] and player_pos[1] == stone_pos[1]:
                action_string.append('L')
            elif player_pos[0] < stone_pos[0] and player_pos[1] == stone_pos[1]:
                action_string.append('R')
        else:
            if player_pos[0] == action[0] and player_pos[1] > action[1]:
                action_string.append('u')
            elif player_pos[0] == action[0] and player_pos[1] < action[1]:
                action_string.append('d')
            elif player_pos[0] > action[0] and player_pos[1] == action[1]:
                action_string.append('l')
            elif player_pos[0] < action[0] and player_pos[1] == action[1]:
                action_string.append('r')

        # Update state for next action
        state = child_node(problem, Node(state), action).state

    return action_string

# Calculate total weight in final step
def calculate_total_weight(solution_path, problem):
    total_weight = 0
    state = problem.initial_state

    for action in solution_path:
        player_pos, stones = state['player_pos'], state['stones']

        if tuple(action) in stones:
            stone_pos = action
            total_weight += stones[stone_pos]

        state = child_node(problem, Node(state), action).state

    return total_weight

def save_output_to_file(input_file_name, algorythm_name, solution_path, total_weight_pushed, num_steps, nodes_generated, total_time_ms, peak_memory_mb, problem):
    # Extract the suffix from the input file name (e.g., xx from inputxx.txt)
    file_suffix = os.path.splitext(os.path.basename(input_file_name))[0].replace("input", "")
    output_file_name = f"output{file_suffix}.txt"
    
    # Create the output directory if it doesn't exist
    output_directory = "output"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Full path for the output file
    output_file_path = os.path.join(output_directory, output_file_name)
    
    # Write the results to the output file
    with open(output_file_path, 'w') as file:
        file.write(algorythm_name + "\n")
        file.write(f"Steps: {num_steps}, Weight: {total_weight_pushed}, Node: {nodes_generated}, Time (ms): {total_time_ms:.2f}, Memory (MB): {peak_memory_mb:.2f}\n")
        file.write(''.join(generate_action_string(solution_path, problem)) + '\n')
        

def compute_total_weight_pushed(solution_path, start_node):
    total_weight_pushed = 0
    state = start_node.state.copy()  
    stones = state['stones'].copy() 

    for action in solution_path:
        player_pos = state['player_pos']

        if tuple(action) in stones:
            stone_pos = tuple(action)
            total_weight_pushed += stones[stone_pos]
            
            new_stone_pos = list(stone_pos)

            if player_pos[0] == stone_pos[0] and player_pos[1] > stone_pos[1]:
                new_stone_pos[1] -= 1  
            elif player_pos[0] == stone_pos[0] and player_pos[1] < stone_pos[1]:
                new_stone_pos[1] += 1  
            elif player_pos[0] > stone_pos[0] and player_pos[1] == stone_pos[1]:
                new_stone_pos[0] -= 1  
            elif player_pos[0] < stone_pos[0] and player_pos[1] == stone_pos[1]:
                new_stone_pos[0] += 1

            stones[tuple(new_stone_pos)] = stones.pop(stone_pos)

        state['player_pos'] = tuple(action) 

    return total_weight_pushed

def process_solution(node, start_time, start_node, algorithm_name, nodes_generated, problem):
    solution_path = solution(node)
    
    end_time = time.time()
    current, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    num_steps = len(solution_path)
    total_time_ms = (end_time - start_time) * 1000  
    peak_memory_mb = peak_memory / (1024 * 1024)  
    
    total_weight_pushed = compute_total_weight_pushed(solution_path, start_node)
    
    save_output_to_file('input02.txt', algorithm_name, solution_path, total_weight_pushed, num_steps, nodes_generated, total_time_ms, peak_memory_mb, problem)

    return solution_path