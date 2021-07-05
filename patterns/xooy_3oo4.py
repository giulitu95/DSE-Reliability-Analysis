#!/usr/bin/env python

from patterns import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.voter2 import Voter2
from pysmt.shortcuts import *

__author__ = "Antonio Tierno"


class Xooy_3oo4_Definition(PatternDefinition):
    """
    Definition for pattern X-o-o-Y V3oo4
    """
    def __init__(self, comp_name: str, comp_n_inputs: int, modules_f_atoms: list, voter_f_atom: Symbol):
        """
        Create a definition for pattern  X-o-o-Y V3oo4
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voter_f_atom: fault atom associated to the voter
        """

        self._modules_f_atoms = modules_f_atoms
        self._voter_f_atom = voter_f_atom
        super(Xooy_3oo4_Definition, self).__init__(comp_name, comp_n_inputs, modules_f_atoms + [voter_f_atom], PatternType.Xooy_3oo4)
        pt_name = self._pt_type.name
        assert len(modules_f_atoms) == 4, "[" + pt_name + "] pattern has 4 modules, choose a correct number of fault atoms"
        self._pt_name = pt_name

    def create(self, nominal_mod_beh) -> Pattern:
        return Xooy_3oo4(self._comp_name, self._comp_n_inputs, self._modules_f_atoms, self._voter_f_atom, nominal_mod_beh)

    @property
    def modules_f_atoms(self) -> list:
        """
        :return: list of fault atoms related to the modules of the patterns
        """
        return self._modules_f_atoms

    @property
    def voter_f_atom(self) -> Symbol:
        """
        :return: fault atom related to the voter of the pattern
        """
        return self._voter_f_atom


class Xooy_3oo4(Pattern):
    """
    Represent a pattern of type tmr-v123
    """
    n_f_atoms = 5

    def __init__(self, comp_name: str, comp_n_inputs: int, modules_fault_atoms: list, voter_fault_atom: Symbol, nominal_mod_beh: Symbol):
        """
        Creata XooY_3oo4 pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param voters_fault_atoms: list of fault atoms associated to the voters
        :param nominal_mod_beh: nominal behavior of the modules
        """
        pattern_name = comp_name + "." + PatternType.Xooy_3oo4.name
        modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx], nominal_mod_beh) for idx in range(4)]

        # The output of the modules are the inputs of the voters
        modules_out_ports = []
        for module in modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 4, "[" + pattern_name + "] The voters must have 4 inputs"
        self._voter = Voter2(pattern_name + ".V", voter_fault_atom, input_ports=modules_out_ports)

        # Output port of the pattern corresponds to the output port of the voter
        output_ports = self._voter.output_ports
        super(Xooy_3oo4, self).__init__(pattern_name, PatternType.Xooy_3oo4, modules_fault_atoms + [voter_fault_atom],
                                      modules, output_ports)

        # Define behavior formula: And of subcomponents' behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in modules]
        # Voter
        subcomp_beh_formula.append(self._voter.behaviour_formula)
        self._behaviour_formula = And(subcomp_beh_formula)



# Test - Example
if __name__ == "__main__":
    nominal_beh = Symbol("nom-beh", FunctionType(REAL, [REAL]))
    ptn = Xooy_3oo4("C1", 1, [Symbol("F0"), Symbol("F1"), Symbol("F2"), Symbol("F3")], Symbol("F_V"), nominal_beh)
    print(ptn.behaviour_formula.serialize())
