from utils import *
import heapq

# A* Search (UCS) Algorithm
def a_star(problem):
    start_node = Node(problem.initial_state)

    frontier = [(0, start_node)]
    explored = {start_node: (0, None)}

    while frontier:
        current_cost, node = heapq.heappop(frontier)

        if problem.goal_test(node.state):
            return solution(node)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action, use_heuristic=True)

            if child not in explored or child.f < explored[child][0]:
                explored[child] = (child.f, node)
                heapq.heappush(frontier, (child.f, child))
    
    return None