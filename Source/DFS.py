from utils import *

def dfs(problem,output_content):

    start_node = Node(problem.initial_state)
    algorithm_name = 'DFS'

    frontier = []
    explored = set()

    tracemalloc.start() 
    start_time = time.time()
    
    frontier.append(start_node)
    
    nodes_generated = 0 

    while frontier:
        node = frontier.pop()

        if problem.goal_test(node.state):
            return process_solution(node, start_time, start_node, algorithm_name, nodes_generated, problem,output_content)
        
        explored.add(node)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            nodes_generated += 1

            if child not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return process_solution(child, start_time, start_node, algorithm_name, nodes_generated, problem,output_content)
                frontier.append(child)
    
    return None