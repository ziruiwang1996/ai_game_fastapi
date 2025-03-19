import sys
import numpy as np

def simple_evaluator(game, state):
    # always estimates 0 utility for non-game-over states at the depth limit
    return 0

def better_evaluator(game, state):
    # Implement a better evaluation function that outperforms the simple one.
    pass

def minimax(game, state, max_depth=-1, evaluation_function=simple_evaluator, alpha=-np.inf, beta=np.inf):
    """
    depth-limited minimax with alpha-beta pruning and evaluation function
    default max_depth = -1 will not impose any depth limit
    default evaluation_function assigns zero to all states
    custom evaluation_function should accept game, state as input and return a number
    minimax returns (child state, child utility, node_count), where:
    - child_state is optimal child
    - child_utility is its utility (also the utility of the parent)
    - node_count is the total number of game states processed by the recursion
    """
    # default evaluation
    if evaluation_function is None: evaluation_function = (lambda g, s: 0)

    # base cases
    if game.is_over_in(state): return None, game.score_in(state)
    if max_depth == 0: return None, evaluation_function(game, state)

    # setup alpha-beta pruning variables
    is_max = game.is_max_turn_in(state)
    bound = -np.inf if is_max else np.inf # bound is "v" in the minimax slides

    # recursive case
    children = []
    utilities = []
    for action in game.valid_actions_in(state):
        # recursively calculate child state utilities and node counts
        child_state = game.perform(action, state)
        _, utility = minimax(game, child_state, max_depth-1, evaluation_function, alpha, beta)

        # save results 
        children.append(child_state)
        utilities.append(utility)

        # add code here for alpha-beta pruning
        # You can use similar code to the minimax slides, except:
        # - do not call minimax again, use the utility computed recursively above
        # - break the loop instead of returning from the function
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

    # return the results
    if is_max:
        best_index = np.argmax(utilities)
    else:
        best_index = np.argmin(utilities)

    return children[best_index], utilities[best_index]

def human_turn(game, state):
    # helper to run a human-controlled turn
    # Show human valid actions
    valid_actions = game.valid_actions_in(state)
    print('actions', valid_actions)

    # Ask human for move (repeat if their input is invalid)
    while True:
        try:
            action = tuple(map(int, input("Enter action in format '<row>,<col>': ").split(",")))
            if action not in valid_actions: raise ValueError
            break
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print("Invalid action, try again.")

    # return new state after turn
    state = game.perform(action, state)
    return state