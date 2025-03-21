import numpy as np
import math
import heapq as hq
from collections import deque
import matplotlib.pyplot as pt
from typing import Callable

WALL, CHARGER, CLEAN, DIRTY = 0, 1, 2, 3

class RoombaDomain:
    def __init__(self, row:int, col:int, max_power:int):
        # deterministic grid world
        num_rows, num_cols = row, col
        grid = CLEAN*np.ones((num_rows, num_cols), dtype=int)
        grid[row//2, 1:col-1] = WALL
        grid[1:row//2+1,col//2] = WALL
        grid[0,0] = CHARGER
        grid[0,-1] = CHARGER
        grid[-1,col//2] = CHARGER
        self.grid = grid
        self.max_power = max_power

    def pack(self, g:np.ndarray, r:int, c:int, p:int) -> tuple[bytes, int, int, int]:
        return (g.tobytes(), r, c, p)
    
    def unpack(self, state:tuple[bytes, int, int, int]) -> tuple[np.ndarray, int, int, int]:
        grid, r, c, p = state
        grid = np.frombuffer(grid, dtype=int).reshape(self.grid.shape).copy()
        return grid, r, c, p

    def initial_state(self, 
                      roomba_position:tuple, 
                      dirty_positions:np.ndarray) -> tuple[bytes, int, int, int]:
        r, c = roomba_position
        grid = self.grid.copy()
        for dr, dc in dirty_positions: grid[dr, dc] = DIRTY
        return self.pack(grid, r, c, self.max_power)

    def render(self, ax:Callable, state:np.ndarray, x=0, y=0)->None:
        grid, r, c, p = self.unpack(state)
        num_rows, num_cols = grid.shape
        ax.imshow(grid, cmap='gray', vmin=0, vmax=3, extent=(x-.5,x+num_cols-.5, y+num_rows-.5, y-.5))
        for col in range(num_cols+1): pt.plot([x+ col-.5, x+ col-.5], [y+ -.5, y+ num_rows-.5], 'k-')
        for row in range(num_rows+1): pt.plot([x+ -.5, x+ num_cols-.5], [y+ row-.5, y+ row-.5], 'k-')
        pt.text(c-.25, r+.25, str(p), fontsize=24)
        pt.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)

    def valid_actions(self, state:np.ndarray) -> list[tuple[tuple[int, int], int]]:
        # r, c is the current row and column of the roomba
        # p is the current power level of the roomba
        # grid[i,j] is WALL, CHARGER, CLEAN or DIRTY to indicate status at row i, column j.
        grid, r, c, p = self.unpack(state)
        num_rows, num_cols = grid.shape
        actions = [((0, 0), 1)]
        if not p:
            return actions
        # Update the list of valid actions 
        # actions[k] has the form ((dr, dc), step_cost) for the kth valid action
        # where dr, dc are the change to roomba's row and column position
        if r-1 >= 0 and grid[r-1, c] != WALL: 
            actions.append(((-1, 0), 1))
        if r+1 < num_rows and grid[r+1, c] != WALL: 
            actions.append(((1, 0), 1))
        if c-1 >= 0 and grid[r, c-1] != WALL: 
            actions.append(((0, -1), 1))
        if c+1 < num_cols and grid[r, c+1] != WALL: 
            actions.append(((0, 1), 1))
        return actions
    
    def perform_action(self, state:np.ndarray, action:tuple[int, int]) -> np.ndarray:
        grid, r, c, p = self.unpack(state)
        dr, dc = action
        # update grid, r, c, and p 
        if dr == 0 and dc == 0:
            if grid[r, c] == CHARGER and p < self.max_power:
                p += 1
            if p and grid[r, c] == DIRTY:
                grid[r, c] = CLEAN
                p -= 1
        else:
            r, c = r+dr, c+dc
            p = p-1
        new_state = self.pack(grid, r, c, p)
        return new_state

    def is_goal(self, state:np.ndarray) -> bool:
        grid, r, c, p = self.unpack(state)
        # In a goal state, no grid cell should be dirty
        all_cleaned = (grid != DIRTY).all()
        # ensure roomba is back at a charger
        return all_cleaned and grid[r, c] == CHARGER

    def simple_heuristic(self, state:np.ndarray) -> int:
        grid, r, c, p = self.unpack(state)
        # get list of dirty positions
        # dirty[k] has the form (i, j)
        # where (i, j) are the row and column position of the kth dirty cell
        dirty = list(zip(*np.nonzero(grid == DIRTY)))
        # if no positions are dirty, estimate zero remaining cost to reach a goal state
        if len(dirty) == 0: return 0
        # otherwise, get the distance from the roomba to each dirty square
        dists = [max(np.fabs(dr-r), np.fabs(dc-c)) for (dr, dc) in dirty]
        # estimate the remaining cost to goal as the largest distance to a dirty position
        return int(max(dists))

    def better_heuristic(self, state:np.ndarray) -> int:
        # a more memory-efficient heuristic than simple_heuristic (fewer popped nodes during A* search)
        grid, r, c, p = self.unpack(state)
        dirty = list(zip(*np.nonzero(grid == DIRTY)))
        if len(dirty) == 0: return 0
        dists = [math.sqrt(pow(abs(dr-r), 2)+pow(abs(dc-c), 2)) for (dr, dc) in dirty]
        return int(max(dists))
    
class SearchNode(object):
    def __init__(self, problem, state, parent=None, action=None, step_cost=0, depth=0):
        self.problem = problem
        self.state = state
        self.parent = parent
        self.action = action
        self.step_cost = step_cost
        self.path_cost = step_cost + (0 if parent is None else parent.path_cost)
        self.path_risk = self.path_cost + problem.heuristic(state)
        self.depth = depth
        self.child_list = []

    def is_goal(self):
        return self.problem.is_goal(self.state)
    
    def children(self):
        if len(self.child_list) > 0: return self.child_list
        domain = self.problem.domain
        for action, step_cost in domain.valid_actions(self.state):
            new_state = domain.perform_action(self.state, action)
            self.child_list.append(
                SearchNode(self.problem, new_state, self, action, step_cost, depth=self.depth+1))
        return self.child_list
    
    def path(self):
        if self.parent == None: return []
        return self.parent.path() + [self.action]

class SearchProblem(object):
    def __init__(self, domain, initial_state, is_goal = None):
        if is_goal is None: is_goal = lambda s: False
        self.domain = domain
        self.initial_state = initial_state
        self.is_goal = is_goal
        self.heuristic = lambda s: 0

    def root_node(self):
        return SearchNode(self, self.initial_state)

class FIFOFrontier:
    def __init__(self):
        self.queue_nodes = deque()
        self.queue_states = set()

    def __len__(self):
        return len(self.queue_states)
    
    def push(self, node):
        if node.state not in self.queue_states:
            self.queue_nodes.append(node)
            self.queue_states.add(node.state)

    def pop(self):
        node = self.queue_nodes.popleft()
        self.queue_states.remove(node.state)
        return node
    
    def is_not_empty(self):
        return len(self.queue_nodes) > 0

class PriorityHeapFIFOFrontier(object):
    def __init__(self):
        self.heap = []
        self.state_lookup = {}
        self.count = 0

    def push(self, node):
        if node.state in self.state_lookup:
            entry = self.state_lookup[node.state] # = [risk, count, node, removed]
            if entry[0] <= node.path_risk: return
            entry[-1] = True # mark removed
        new_entry = [node.path_risk, self.count, node, False]
        hq.heappush(self.heap, new_entry)
        self.state_lookup[node.state] = new_entry
        self.count += 1

    def pop(self):
        while len(self.heap) > 0:
            risk, count, node, already_removed = hq.heappop(self.heap)
            if not already_removed:
                self.state_lookup.pop(node.state)
                return node

    def is_not_empty(self):
        return len(self.heap) > 0

    def states(self):
        return list(self.state_lookup.keys())