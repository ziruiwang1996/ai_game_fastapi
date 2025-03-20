import numpy as np
from scipy.signal import correlate

# enum for grid cell contents
EMPTY = 0
MAX = +1
MIN = -1

class GomokuDomain:
    def __init__(self, board_size, win_size):
        self.board_size = board_size
        self.win_size = win_size

    def initial_state(self):
        return np.full((self.board_size, self.board_size), EMPTY)

    def is_max_turn_in(self, state):
        return (state == MAX).sum() == (state == MIN).sum()

    def current_player_in(self, state):
        return MAX if self.is_max_turn_in(state) else MIN

    def valid_actions_in(self, state):
        return list(zip(*np.nonzero(state == EMPTY)))

    def perform(self, action, state):
        new_state = state.copy()
        new_state[action] = MAX if self.is_max_turn_in(state) else MIN
        return new_state

    def score_in(self, state):
        win_patterns = [
            np.rot90(np.ones((1, self.win_size))), # vertical
            # add three more win patterns for horizontal, diagonal, and anti-diagonal
            # the functions np.rot90, np.ones, and np.eye may be helpful
            np.ones((1, self.win_size)),
            np.eye(self.win_size), 
            np.rot90(np.eye(self.win_size))
        ]

        for pattern in win_patterns:
            matches = correlate(state, pattern, mode='valid', method='direct')
            if (matches == +self.win_size).any(): return +1
            if (matches == -self.win_size).any(): return -1

        return 0

    def is_over_in(self, state):
        draw = (state != EMPTY).all()
        return draw or self.score_in(state) != 0
    
    def is_draw(self, state):
        return (state != EMPTY).all()