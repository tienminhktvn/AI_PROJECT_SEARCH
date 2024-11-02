from utils import *

def bfs(problem, output_content):
    if timeout_event.is_set():  # Kiểm tra nếu event đã được đặt
        print("timeout in bfs")
        return None
    #Set timeout thread
    timeout_thread = threading.Thread(target=time_limit_check)
    timeout_thread.start()
    
    print('calculating bfs')
    start_node = Node(problem.initial_state)
    algorithm_name = 'BFS'

    frontier = []
    explored = set()

    tracemalloc.start() 
    start_time = time.time()
    
    frontier.append(start_node)
    
    nodes_generated = 0  

    while frontier:
        if timeout_event.is_set():  # Kiểm tra nếu event đã được đặt
            stop_timeout_event.set()
            timeout_thread.join()
            stop_timeout_event.clear()
            timeout_event.clear()
            output_content.append(algorithm_name)
            output_content.append("Timeout")
            print("timeout in bfs")
            return None
        
        node = frontier.pop(0)

        if problem.goal_test(node.state):
            stop_timeout_event.set()
            timeout_thread.join()
            stop_timeout_event.clear()
            timeout_event.clear()
            return process_solution(node, start_time, start_node, algorithm_name, nodes_generated, problem,output_content)
        
        explored.add(node)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            nodes_generated += 1

            if child not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    stop_timeout_event.set()
                    timeout_thread.join()
                    stop_timeout_event.clear()
                    timeout_event.clear()
                    return process_solution(child, start_time, start_node, algorithm_name, nodes_generated, problem,output_content)
                frontier.append(child)
    
    return None