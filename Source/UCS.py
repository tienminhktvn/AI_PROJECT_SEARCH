from utils import *
import heapq

# Uniform Cost Search (UCS) Algorithm
def ucs(problem):
    start_node = Node(problem.initial_state)

    frontier = []
    explored = set()

    heapq.heappush(frontier, (start_node.cost, start_node))

    while frontier:
        current_cost, node = heapq.heappop(frontier)

        if problem.goal_test(node.state):
            return solution(node)
        
        explored.add(str(node.state))

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)

            if str(child.state) not in explored:
                heapq.heappush(frontier, (child.cost, child))
            else:
                for i, (existing_cost, existing_node) in enumerate(frontier):
                    if existing_node.state == child.state and child.cost < existing_cost:
                        frontier[i] = (child.cost, child) 
                        heapq.heapify(frontier)
                        break
    
    return None