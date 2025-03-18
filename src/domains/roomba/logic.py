from .models import FIFOFrontier, PriorityHeapFIFOFrontier
from .models import RoombaDomain, SearchProblem, CLEAN
import matplotlib.pyplot as pt
from matplotlib import animation
import numpy as np
import io
import tempfile
import os

def queue_search(frontier, problem):
    # Update implementation to also return node count
    # This is the total number of nodes popped off the frontier during the search
    count = 0
    explored = set()
    root = problem.root_node()
    frontier.push(root)
    while frontier.is_not_empty():
        node = frontier.pop() # need to count how many times this happens
        count += 1
        if node.is_goal(): break
        explored.add(node.state)
        for child in node.children():
            if child.state in explored: continue
            frontier.push(child)
    plan = node.path() if node.is_goal() else []
    # Second return value should be node count, not 0
    return plan, count

def breadth_first_search(problem):
    return queue_search(FIFOFrontier(), problem)

def a_star_search(problem, heuristic):
    problem.heuristic = heuristic
    return queue_search(PriorityHeapFIFOFrontier(), problem)

def get_path(row:int, col:int, max_power:int):
    # set up initial state by making five random open positions dirty
    domain = RoombaDomain(row, col, max_power)
    init = domain.initial_state(
        roomba_position = (0, 0),
        dirty_positions = np.random.permutation(list(zip(*np.nonzero(domain.grid == CLEAN))))[:5])

    problem = SearchProblem(domain, init, domain.is_goal)
    plan, node_count = a_star_search(problem, domain.better_heuristic)

    # reconstruct the intermediate states along the plan
    states = [ problem.initial_state]
    for a in range(len(plan)):
        states.append(domain.perform_action(states[-1], plan[a]))

    fig = pt.figure(figsize=(8,8))
    def drawframe(n):
        pt.cla()
        domain.render(pt.gca(), states[n])
    anim = animation.FuncAnimation(fig, drawframe, frames=len(states), interval=500, blit=False)

    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as temp_file:
        temp_path = temp_file.name  # Store the file path
    try:
        anim.save(temp_path, writer="pillow")  # Save as GIF
        # Read file into BytesIO
        buffer = io.BytesIO()
        with open(temp_path, "rb") as f:
            buffer.write(f.read())
        buffer.seek(0)  # Reset buffer for reading
    except Exception as e:
        print(f"Error saving GIF: {e}")
    finally:
        os.remove(temp_path)  # Delete the temp file
        
    return buffer