import numpy as np
from .models import GomokuDomain

def simple_evaluator(game, state:np.ndarray):
    # always estimates 0 utility for non-game-over states at the depth limit
    return 0

def better_evaluator(game, state:np.ndarray):
    # placeholder for a better evaluation function that outperforms the simple one.
    pass

def minimax(game:GomokuDomain, 
            state:np.ndarray, 
            max_depth=-1, 
            evaluation_function=simple_evaluator, 
            alpha=-np.inf, 
            beta=np.inf) -> tuple[np.ndarray, int]:
    """
    depth-limited minimax with alpha-beta pruning and evaluation function
    default max_depth = -1 will not impose any depth limit
    default evaluation_function assigns zero to all states
    custom evaluation_function should accept game, state as input and return a number
    minimax returns (child state, child utility), where:
    - child_state is optimal child
    - child_utility is its utility (also the utility of the parent)
    """
    # default evaluation
    if evaluation_function is None: evaluation_function = (lambda g, s: 0)

    # base cases
    if game.is_over_in(state): return None, game.score_in(state)
    if max_depth == 0: return None, evaluation_function(game, state)

    # setup alpha-beta pruning variables
    is_max = game.is_max_turn_in(state)
    bound = -np.inf if is_max else np.inf 

    # recursive case
    curMinChild, curMinUtility = None, np.inf
    curMaxChild, curMaxUtility = None, -np.inf
    for action in game.valid_actions_in(state):
        child_state = game.perform(action, state)
        _, utility = minimax(game, child_state, max_depth-1, evaluation_function, alpha, beta)

        if utility < curMinUtility:
            curMinChild, curMinUtility = child_state, utility
        if utility > curMaxUtility:
            curMaxChild, curMaxUtility = child_state, utility

        # alpha-beta pruning
        if is_max:
            bound = max(bound, utility)
            alpha = max(alpha, bound)
            if utility >= beta:
                break
        else:
            bound = min(bound, utility)
            beta = min(beta, bound)
            if utility <= alpha:
                break

    if is_max:
        return curMaxChild, curMaxUtility
    else:
        return curMinChild, curMinUtility