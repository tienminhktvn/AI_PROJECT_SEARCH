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
    def __init__(self, state, parent=None, action=None, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost                        # g(n)
        self.heuristic = heuristic              # Heuristic h(n)
        self.f = self.cost + self.heuristic     # f(n) = g(n) + h(n)

    def __lt__(self, other):
        return self.f < other.f

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

                    if self.board[new_stone_pos[1]][new_stone_pos[0]] == '#':
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
                    distance = manhattan_distance(stone, switch)
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