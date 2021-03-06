#!/usr/bin/env python3
"""
politicalSine.py
A mathematical model to show the general polarization,
or lack thereof, of a representative republic.
"""
import numpy as np
import indra.prop_args2 as props

MODEL_NM = "politicalSine"

AGENT_NUM = 0

NUM_OF_AGENTS = 100
PERCENTAGE_OF_OLIGARCHS = 10 / 100
OLIGARCH_NUM = int(PERCENTAGE_OF_OLIGARCHS*NUM_OF_AGENTS)

if OLIGARCH_NUM == 0:
    OLIGARCH_NUM += 1

CITIZEN_NUM = NUM_OF_AGENTS - OLIGARCH_NUM + 1

OLIGARCH_POL_BIAS = 3
CITIZEN_POL_BIAS = -3
OLIGARCH_WEALTH_BIAS = 3
CITIZEN_WEALTH_BIAS = -3

OLIGARCH_POL_BELL = np.random.normal(OLIGARCH_POL_BIAS, 1, OLIGARCH_NUM)
CITIZEN_POL_BELL = np.random.normal(CITIZEN_POL_BIAS, 1, CITIZEN_NUM)
OLIGARCH_WEALTH_BELL = np.random.normal(OLIGARCH_WEALTH_BIAS, 1, OLIGARCH_NUM)
CITIZEN_WEALTH_BELL = np.random.normal(CITIZEN_WEALTH_BIAS, 1, CITIZEN_NUM)

def run(prop_dict=None):
    # We need to create props before we import the model,
    # as our choice of display_method is dependent on the user_type.
    pa = props.PropArgs.create_props(MODEL_NM, prop_dict)
    import models.politicalSine as ps
    import indra.utils as utils

    (prog_file, log_file, prop_file, results_file) = utils.gen_file_names(MODEL_NM)

    # Now we create a minimal environment for our agents to act within:
    env = ps.BasicEnv(model_nm=MODEL_NM, props=pa)
    # Now we loop creating multiple agents
    # with numbered names based on the loop variable:
    
    AGENT_NUM = 0
    for i in range(0, CITIZEN_NUM):
        print(CITIZEN_POL_BELL[i])

        env.add_agent(ps.Citizen(name="CITagent"
                                 + str(AGENT_NUM), goal="Voting" + str(CITIZEN_POL_BELL[i]),
                                 political=CITIZEN_POL_BELL[i],
                                 wealth=CITIZEN_WEALTH_BELL[i]
                                 )
                      )
        AGENT_NUM += 1

    for i in range(0, OLIGARCH_NUM):
        env.add_agent(ps.Citizen(name="OLIagent"
                                 + str(AGENT_NUM), goal="Voting" + str(OLIGARCH_POL_BELL[i]),
                                 political=OLIGARCH_POL_BELL[i],
                                 wealth=OLIGARCH_WEALTH_BELL[i]
                                )
                      )
        AGENT_NUM += 1

    return utils.run_model(env, prog_file, results_file)

if __name__ == "__main__":
    run()
