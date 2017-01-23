"""
This is the code for the UCT (Upper Confidence Bounds for Trees)
algorithm.
"""

from ai.node import Node
import copy
import math
import random
from time import process_time


def get_best_move(cur_state, reward_function):
    """
    Gets the AI's best move. Or at least, gets what it thinks is its
    best move.
    The reward_function parameter is a function that evaluates a
    game state with a value in the interval [0, 1], where 0 is bad
    and 1 is good.
    """
    return _uct_search(cur_state, reward_function)


def _uct_search(game_state, reward_function):
    root = Node(game_state)

    print("Root: ", str(root))

    start_time = process_time()
    while _within_computational_budget(start_time):
        print("Still going...")
        v = _tree_policy(root)
        print("Tree policy selected this node: ", str(v))
        delta = _default_policy(v.state, reward_function)
        print("Delta: ", str(delta))
        _back_up(v, delta)
 
    # This will usually, but not always, return the action that leads
    # to the child with the highest reward. It COULD (since Cp is set
    # to zero for this call) return the node that is most visited instead.
    # This is often the node that is the best, but not always. So,
    # one possible improvement is to check if the most visited root
    # action is not also the one with the highest reward, and if it isn't,
    # keep searching.
    return _best_child(v, 0).incoming_action






def _back_up(v, delta):
    """
    Give delta to each node in the visit from the newly added node v
    to the root.
    Delta is the value of the terminal node that we reached through v.
    """
    while v is not None:
        # num_times_visited is N in the algorithm
        # total_reward is Q, the total reward of all payouts so far pased
        # through this state
        v.num_times_visited += 1
        v.total_reward += _delta_function(delta, v)
        v = v.parent


def _best_child(v, c):
    def valfunc(v_prime, v):
        left = v_prime.total_reward / v_prime.num_times_visited
        right = c * math.sqrt((2 * math.ln(v.num_times_visited))\
                / v_prime.num_times_visited)
        return left + right
    values_and_nodes = [(valfunc(v_prime, v), v_prime) for v_prime\
            in v.children]
    max_val = max(values_and_nodes, key=lambda tup: tup[0])
    for tup in values_and_nodes:
        if tup[0] == max_val:
            return tup[1]

    # This should never be reached
    assert(False)


def _choose_untried_action_from(available_actions):
    # This is one place to put a neural network: we need a good way
    # of choosing an untried action, rather than just uniform random
    return random.choice(available_actions)


def _default_policy(game_state, reward_function):
    while not game_state.game_over():
        # This function should be replaced with the policy network
        action = random.choice(game_state.possible_moves())
        game_state = copy.deepcopy(game_state)
        game_state.take_turn(action)
    return reward_function(game_state)


def _delta_function(delta, v):
    """
    Denotes the component of the of the reward vector delta associated
    with the current player p at node v
    """
    # This may need to change in a game that is for more than two players.
    # It should return a value that takes into account how well each
    # player is doing - so teammates should be maximized while enemies
    # are minimized or whatever.
    # But for two player games, you can simply return delta.
    return delta


def _expand(v):
    available_actions = v.state.available_actions()
    action_to_try = _choose_untried_action_from(available_actions)
    v_prime = v.derive_child(action_to_try)
    return v_prime


def _tree_policy(v):
    # This value of Cp works for rewards in the range of [0, 1]
    Cp = 1 / math.sqrt(2)
    while v.is_non_terminal():
        if v.is_not_fully_expanded():
            return _expand(v)
        else:
            v = _best_child(v, Cp)
    return v


def _within_computational_budget(start):
    """
    Returns True if time still hasn't run out for the computer's turn.
    """
    elapsed_time = process_time() - start
    return elapsed_time < 0.5
    


