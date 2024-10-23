from utils import *

def dfs(problem):
    start_node = Node(problem.initial_state)

    frontier = []
    explored = {start_node: 'visited'}

    frontier.append(start_node)

    while frontier:
        node = frontier.pop()

        if problem.goal_test(node.state):
            return solution(node)
        
        explored[node] = 'visited'

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)

            if child not in explored:
                frontier.append(child)
    
    return None