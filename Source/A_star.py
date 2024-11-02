from utils import *

# A* Search Algorithm
def a_star(problem, output_content):
    if timeout_event.is_set():  # Kiểm tra nếu event đã được đặt
        print("timeout in a*")
        return None
    
    print('calculating a*')
    start_node = Node(problem.initial_state)
    algorithm_name = 'A*'

    tracemalloc.start() 
    start_time = time.time()
    
    frontier = [(0, start_node)]
    explored = {start_node: (0, None)}
    
    nodes_generated = 0  

    while frontier:
        if timeout_event.is_set():  # Kiểm tra nếu event đã được đặt
            return None
        
        current_cost, node = heapq.heappop(frontier)

        if problem.goal_test(node.state):
            return process_solution(node, start_time, start_node, algorithm_name, nodes_generated, problem, output_content)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action, use_heuristic=True)
            nodes_generated += 1

            if child not in explored or child.f < explored[child][0]:
                explored[child] = (child.f, node)
                heapq.heappush(frontier, (child.f, child))
    
    return None
