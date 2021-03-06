#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 21:39:40 2015

@author: Brandon Logan and Gene Callahan

Segregation Run File
"""

import indra.prop_args2 as props
import os

MODEL_NM = "segregation"


def run(prop_dict=None):
    pa = props.PropArgs.create_props(MODEL_NM, prop_dict)

    import indra.utils as utils
    import schelling.segregation as sm

    # set up some file names:
    (prog_file, log_file, prop_file, results_file) = utils.gen_file_names(MODEL_NM)
    # We store basic parameters in a "property" file; this allows us to save
    #  multiple parameter sets, which is important in simulation work.
    #  We can read these in from file or set them here.

    if pa["user_type"] == props.WEB:
        pa["base_dir"] = os.environ['base_dir']
        
    # Now we create an environment for our agents to act within:
    env = sm.SegregationEnv("A city",
                            pa["grid_width"],
                            pa["grid_height"],
                            model_nm=pa.model_nm,
                            props=pa)
    
    # Now we loop creating multiple agents with numbered names
    # based on the loop variable:
    for i in range(pa["num_B_agents"]):
        env.add_agent(sm.BlueAgent(name="Blue agent" + str(i),
                      goal="A good neighborhood.",
                      min_tol=pa['min_tolerance'],
                      max_tol=pa['max_tolerance'],
                      max_detect=pa['max_detect']))
        
    for i in range(pa["num_R_agents"]):
        env.add_agent(sm.RedAgent(name="Red agent" + str(i),
                      goal="A good neighborhood.",
                      min_tol=pa['min_tolerance'],
                      max_tol=pa['max_tolerance'],
                      max_detect=pa['max_detect']))
        
    return utils.run_model(env, prog_file, results_file)

if __name__ == "__main__":
    run()
