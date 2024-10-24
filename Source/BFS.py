from utils import *
import time
import tracemalloc

def bfs(problem):
    start_node = Node(problem.initial_state)
    algorithm_name = 'BFS'

    frontier = []
    explored = {start_node: 'visited'}
    
    tracemalloc.start() 
    start_time = time.time()

    frontier.append(start_node)
    
    total_weight_pushed = 0 
    nodes_generated = 0  
    
    while frontier:
        node = frontier.pop(0)

        if problem.goal_test(node.state):
            solution_path = solution(node)
            
            end_time = time.time()
            current, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            num_steps = len(solution_path)
            total_time_ms = (end_time - start_time) * 1000  
            peak_memory_mb = peak_memory / (1024 * 1024)  
            
            total_weight_pushed = 0

            # Calculate total weight pushed for the solution path
            total_weight_pushed = compute_total_weight_pushed(solution_path, start_node)

            # Write results to output file
            save_output_to_file('input02.txt', algorithm_name, solution_path, total_weight_pushed, num_steps, nodes_generated, total_time_ms, peak_memory_mb, problem)

            return solution_path
        
        explored[node] = 'visited'

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            nodes_generated += 1

            if child not in explored:
                frontier.append(child)
    
    return None