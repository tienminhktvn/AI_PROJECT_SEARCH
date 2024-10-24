from utils import *
import heapq
import time
import tracemalloc


# A* Search (UCS) Algorithm
def a_star(problem):
    start_node = Node(problem.initial_state)
    
    # Initialize performance tracking
    tracemalloc.start()  # Start memory tracking
    start_time = time.time()  # Start time tracking

    frontier = []
    explored = set()
    total_weight_pushed = 0 
    nodes_generated = 0  

    heapq.heappush(frontier, (start_node.cost, start_node))
    while frontier:
        current_cost, node = heapq.heappop(frontier)

        if problem.goal_test(node.state):
            solution_path = solution(node)
            
            # Performance measurement
            end_time = time.time()
            current, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Calculate statistics
            num_steps = len(solution_path)
            total_time_ms = (end_time - start_time) * 1000  
            peak_memory_mb = peak_memory / (1024 * 1024)  
            
            # Write results to output file
            save_output_to_file('input02.txt', solution_path, total_weight_pushed, num_steps, nodes_generated, total_time_ms, peak_memory_mb, problem)

            return solution_path
        
        explored.add(str(node.state))

        for action in problem.actions(node.state):
            child = child_node(problem, node, action, use_heuristic=True)
            nodes_generated += 1

            # Check if pushing a stone to calculate total weight
            if action in node.state['stones']:
                total_weight_pushed += node.state['stones'][tuple(action)]

            if str(child.state) not in explored:
                heapq.heappush(frontier, (child.cost, child))
            else:
                for i, (existing_cost, existing_node) in enumerate(frontier):
                    if existing_node.state == child.state and child.cost < existing_cost:
                        frontier[i] = (child.cost, child) 
                        heapq.heapify(frontier)
                        break
    
    return None

