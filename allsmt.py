#!/usr/bin/env python

import mathsat
from pysmt.shortcuts import *
import datetime as dt

__author__ = "Giuliano Turri"

# Define callback called each time mathsat finds a new model
def callback(model, converter, result, model_counter, start_time):
    # Convert back the mathsat model to a pySMT formula
    py_model = [converter.back(v) for v in model]
    # Append the module to the result list
    result.append(And(py_model))
    model_counter[0] = model_counter[0] + 1
    time_diff =  dt.datetime.today().timestamp() - start_time[0]
    print("[AllSMT] -> " + str(model_counter[0]) + " models [" + str(int(1/time_diff)) + " m/s]", end = "\r", flush=True)
    start_time[0] = dt.datetime.today().timestamp()
    return 1  # go on


def allsmt(formula, to_keep_atoms: list):
    msat = Solver(name="msat")
    converter = msat.converter
    # add the csa formula to the solver
    msat.add_assertion(formula)
    result = []
    model_counter = [0]
    models_sec = [0]
    # Directly invoke mathsat APIs
    print("[AllSMT] Compute allSMT on the formula...")
    start_time = [dt.datetime.today().timestamp()]
    start_interval = [dt.datetime.today().timestamp()]
    mathsat.msat_all_sat(msat.msat_env(),
                         [converter.convert(atom) for atom in to_keep_atoms],
                         # Convert the pySMT term into a MathSAT term
                         lambda model: callback(model, converter, result, model_counter, start_time))
    res_formula = Or(result)
    print("[AllSMT] -> Done! " + str(model_counter[0]) + " models found", flush=True)
    return res_formula