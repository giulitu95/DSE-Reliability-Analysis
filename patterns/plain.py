#!/usr/bin/env python

from patterns import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.voter import Voter
from pysmt.shortcuts import *

__author__ = "Giuliano Turri"


class PlainDefinition(PatternDefinition):
    """
    Definition for pattern TMR-V111
    """
    def __init__(self, comp_name: str, comp_n_inputs: int, f_atom: Symbol):
        """
        Create a definition for pattern TMRV111
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voter_f_atom: fault atom associated to the voter
        """
        self._f_atom = f_atom
        super(PlainDefinition, self).__init__(comp_name,  comp_n_inputs, [f_atom], PatternType.PLAIN)

    def create(self, nominal_mod_beh) -> Pattern:
        return Plain(self._comp_name, self._comp_n_inputs, self.f_atom, nominal_mod_beh)

    @property
    def f_atom(self) -> list:
        """
        :return: list of fault atoms related to the modules of the patterns
        """
        return self._f_atom



class Plain(Pattern):
    """
    Represent a pattern of type tmr-v111
    """
    n_f_atoms = 4

    def __init__(self, comp_name: str, comp_n_inputs: int, fault_atom: Symbol, nominal_mod_beh: Symbol):
        """
        Creata TMR-V111 pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param voter_fault_atom: fault atom associated to the voter
        :param nominal_mod_beh: nominal behaviour of the modules
        """
        pattern_name = comp_name + "." + PatternType.TMR_V111.name
        self._module = FaultyModule(pattern_name + ".M", comp_n_inputs, fault_atom, nominal_mod_beh)
        output_ports = self._module.output_ports
        super(Plain, self).__init__(pattern_name, PatternType.PLAIN, [fault_atom], [self._module], output_ports)

        # Define behaviour formula: And of subcomponents behaviours
        # Modules
        self._behaviour_formula = self._module.behaviour_formula



'''# Test - Example
if __name__ == "__main__":
    nominal_beh = Symbol("nom-beh", FunctionType(REAL, [REAL]))
    plain = Plain("C1", 1, Symbol("F0"), nominal_beh)
    print(plain.behaviour_formula.serialize())'''
