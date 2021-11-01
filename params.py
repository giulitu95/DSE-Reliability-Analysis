#!/usr/bin/env python

from typing import NamedTuple

__author__ = "Giuliano Turri, Antonio Tierno"

'''
Design objectives
'''


class NonFuncParamas(NamedTuple):
    fault_prob: float
    cost: float
    power: float
    size: float
