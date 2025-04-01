import numpy as np
import matplotlib.pyplot as pt

# Domain API
# state (mx, my, cx, cy) are xy positions of mouse and cat
# Each can move one unit vertically, horizontally, or diagonally
# The cat moves uniformly at random, the mouse is the agent
# Reward is maximized by staying far from the cat

# The mouse and cat live in a discrete rectangular grid
# If they try to move outside the grid, they stay where they are
class CatMouseDomain:
    def __init__(self, row:int, col:int):
        self.grid_rows = row
        self.grid_cols = col 
        self.N = (row*col)**2 # Total number of possible states
        self.actions = self.valid_actions()
        self.K = len(self.actions)
        self.r = self.reward_array()
    
    def valid_actions(self):
        # The mouse agent has 9 actions: one unit in each direction, or staying in place
        # dmx and dmy represent changes to position mx and my
        actions = []
        for dmx in [-1,0,1]:
            for dmy in [-1,0,1]:
                actions.append((dmx, dmy))
        return actions

    ### State-index mapping
    # To use the MDP formalism, each state must be assigned a unique index
    # This determines how to fill out the reward, probability, and utility arrays
    # For this domain, we can treat mouse and cat coordinates as digits
    # The base of the digits depends on the grid size
    # For example, in a 10x10 grid, the coordinates are digits in a base-10 number:
    # state mx, my, cx, cy = 0, 0, 0, 0 <-> index 0000
    # state mx, my, cx, cy = 1, 0, 0, 0 <-> index 1000
    def state_to_index(self, state):
        """
        This assigns each state a unique index
        Works essentially like algorithms that convert binary strings to ints,
        except that a non-square grid doesn't have a uniform base for every digit
        The coef variable is analogous to the powers of the base
        The elements of the state tuple are analogous to the digits
        """
        factors = [self.grid_cols, self.grid_rows, self.grid_cols, self.grid_rows]
        idx = 0
        coef = 1
        for i in range(4):
            digit = state[i]
            idx += digit*coef
            coef *= factors[i]
        return int(idx)

    def index_to_state(self, idx):
        """
        This method is the inverse of "state_to_index":
        Given an integer index, it reconstructs the corresponding state.
        Works essentially like algorithms that convert ints to binary strings
        """
        factors = [self.grid_cols, self.grid_rows, self.grid_cols, self.grid_rows]
        state = []
        for i in range(4):
            digit = idx % factors[i]
            idx = (idx - digit) / factors[i]
            state.append(digit)
        return tuple(state)

    ### Reward function
    # Uses the distance from the cat as a reward
    # This will make the mouse stay as far as possible from the cat
    # Since diagonal motions are allowed, this uses the Chebyshev (chessboard) distance:
    # https://en.wikipedia.org/wiki/Chebyshev_distance
    def reward_array(self):
        def reward(state):
            mx, my, cx, cy = state
            return max(np.fabs(mx-cx), np.fabs(my-cy))
        return np.array([reward(self.index_to_state(i)) for i in range(self.N)])

    ### Performing actions
    # Change the mouse coordinates by mdx and mdy
    # Likewise for the cat
    # Cat arguments default to None, in which case the cat motion is randomized
    def move(self, state, mdx, mdy, cdx=None, cdy=None):
        # Randomize cat motions if not provided
        if cdx is None:
            cdx, cdy = np.random.choice([-1,0,1],size=2)
        # Unpack mouse and cat coordinates in the current state
        mx, my, cx, cy = state
        # animals stay at the same place if they try to move past the grid bounds
        mx = min(max(0, mx+mdx), self.grid_cols-1)
        my = min(max(0, my+mdy), self.grid_rows-1)
        cx = min(max(0, cx+cdx), self.grid_cols-1)
        cy = min(max(0, cy+cdy), self.grid_rows-1)
        return (mx, my, cx, cy)

    def plot_state(self, state):
        """
        state = (mx, my, cx, cy)
        Visualize a state with matplotlib:
            Blue circle is mouse
            Red circle is cat
        """
        mx, my, cx, cy = state
        pt.grid()
        pt.scatter(cx, cy, s=600, c='r')
        pt.scatter(mx, my, s=200, c='b')
        pt.xlim([-1, self.grid_cols])
        pt.ylim([-1, self.grid_rows])