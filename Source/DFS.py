from utils import *

def dfs(problem):
    start_node = Node(problem.initial_state)

    frontier = []
    explored = set()

    frontier.append(start_node)

    while frontier:
        node = frontier.pop()

        if problem.goal_test(node.state):
            return solution(node)
        
        explored.add(node)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)

            if child not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return solution(child)
                frontier.append(child)
    
    return None