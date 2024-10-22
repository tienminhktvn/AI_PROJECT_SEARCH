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
        
        explored.add(str(node.state))

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)

            if str(child.state) not in explored:
                frontier.append(child)
    
    return None