"""
utils.py
Various helpful bits that don't fit elsewhere!
"""

import sys
import logging

from indra.prop_args2 import type_dict, PERIODS
import indra.prop_args2 as prop_args
import indra.user as u

# some values useful for checking valid ranges:
BIG_INT = sys.maxsize
BTWN_ZERO_ONE = (.01, .99)
NTRL_NUMS = (0, BIG_INT)
POS_INTS = (1, BIG_INT)
MAX_GRID = 1000
GRID_LIMITS = (1, MAX_GRID)  
MAX_AGENTS = MAX_GRID * MAX_GRID  # enough to fill a maximum sized grid
AGENT_LIMITS = (1, MAX_AGENTS)
WOLFRAM_RULE_LIMITS = (0, 255)


def in_range(low, val, high):
    if all([low, high]):
        return low <= val <= high
    elif low:
        return low <= val
    elif high:
        return val <= high
    else:
        return True
        
def check_val(val, default=None, limits=None):  
    if val is None:
        return False

    if limits is not None:
        (low, high) = limits
        return in_range(low, val, high)
    else:
        return True

def gen_file_names(model_nm):
    """
    Generate our standard list of I/O spots.
    """
    prog_file = model_nm + ".py"
    log_file = model_nm + ".log"
    prop_file = model_nm + ".props"
    rsul_file = model_nm + ".out"
    return (prog_file, log_file, prop_file, rsul_file)


def run_model(env, prog_file, results_file):
    # Logging is automatically set up for the modeler:
    logging.info("Starting program " + prog_file)

    periods = env.props.get(PERIODS)
    if periods is None:
        periods = -1
    else:
        periods = int(periods)
    # And now we set things running!
    try:
        results = env.run(periods=periods)
    except SystemExit:
        pass
    env.record_results(results_file)
    return results


def read_props(model_nm):
    """
    A prop file to read must be our first arg, if it exists.
    """
    if len(sys.argv) > 1:
        poss_props = sys.argv[1]
        if not poss_props.startswith('-'):  # not a property but a prop file
            return prop_args.read_props(model_nm, poss_props)

    return None

