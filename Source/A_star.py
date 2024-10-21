# A* Search Algorithm
# def a_star_search(problem):
#     frontier = []
#     explored = set()

#     start_node = Node(problem.initial_state, cost=0, heuristic=heuristic(problem.initial_state, problem))
#     heapq.heappush(frontier, start_node)

#     while frontier:
#         node = heapq.heappop(frontier)

#         if problem.goal_test(node.state):
#             return solution(node)

#         explored.add(node.state)

#         for action in problem.actions(node.state):
#             new_state = action
#             new_cost = node.cost + 1  # Adjust this based on the game logic
#             new_heuristic = heuristic(new_state, problem)
            
#             child_node = Node(new_state, parent=node, cost=new_cost, heuristic=new_heuristic)

#             if child_node.state not in explored and child_node not in frontier:
#                 heapq.heappush(frontier, child_node)
    
#     return None  # No solution found