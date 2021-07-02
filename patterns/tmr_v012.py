#!/usr/bin/env python

from patterns import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.voter import Voter
from pysmt.shortcuts import *

__author__ = "Antonio Tierno"


class TmrV012Definition(PatternDefinition):
    """
    Definition for pattern TMR-V012
    """
    def __init__(self, comp_name: str, comp_n_inputs: int, modules_f_atoms: list, voters_f_atoms: list):
        """
        Create a definition for pattern TMRV012
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voter_f_atoms: fault atom associated to the voters
        """
        pt_type = PatternType.TMR_V012
        self._modules_f_atoms = modules_f_atoms
        assert len(modules_f_atoms) == 3, "[" + pt_type.name + "] pattern has 3 modules, choose a correct number of fault atoms"
        self._voters_f_atoms = voters_f_atoms
        assert len(voters_f_atoms) == 2, "[" + pt_type.name + "] pattern has 2 voters, choose a correct number of fault atoms"
        super(TmrV012Definition, self).__init__(comp_name, comp_n_inputs, modules_f_atoms + voters_f_atoms, PatternType.TMR_V112)
        self._pt_name = pt_type.name

    def create(self, nominal_mod_beh) -> Pattern:
        return TmrV012(self._comp_name, self._comp_n_inputs, self._modules_f_atoms, self._voters_f_atoms, nominal_mod_beh)

    @property
    def modules_f_atoms(self) -> list:
        """
        :return: list of fault atoms related to the modules of the patterns
        """
        return self._modules_f_atoms

    @property
    def voter_f_atom(self) -> list:
        """
        :return: fault atom related to the voter of the pattern
        """
        return self._voters_f_atoms


class TmrV012(Pattern):
    """
    Represent a pattern of type tmr-v012
    """
    n_f_atoms = 5

    def __init__(self, comp_name: str, comp_n_inputs: int, modules_fault_atoms: list, voters_fault_atoms: list, nominal_mod_beh: Symbol):
        """
        Creata TMR-V012 pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param voters_fault_atoms: list of fault atoms associated to the voters
        :param nominal_mod_beh: nominal behavior of the modules
        """
        pattern_name = comp_name + "." + PatternType.TMR_V112.name
        modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx], nominal_mod_beh) for idx in range(3)]

        # The output of the modules are the inputs of the voters
        modules_out_ports = []
        for module in modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 3, "[" + pattern_name + "] The voters must have 3 inputs"
        voters = [Voter(pattern_name + ".V" + str(idx), voters_fault_atoms[idx], input_ports=modules_out_ports) for idx in range(2)]

        # Output of the pattern corresponds to the output ports of Module1, of voter V1, and of voter V2
        output_ports = []
        output_ports.append(modules_out_ports[0])
        for voter in voters:
            output_ports.extend(voter.output_ports)
        assert len(output_ports) == 3, "[" + pattern_name + "] The pattern must have 3 outputs"
        super(TmrV012, self).__init__(pattern_name, PatternType.TMR_V012, modules_fault_atoms + voters_fault_atoms, modules, output_ports)

        # Define behavior formula: And of subcomponents' behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in modules]
        # Voter
        subcomp_beh_formula.extend([voter.behaviour_formula for voter in voters])
        self._behaviour_formula = And(subcomp_beh_formula)

'''
# Test - Example
if __name__ == "__main__":
    pt012_def = TmrV012Definition("C1", 1, [Symbol("F_M0"), Symbol("F_M1"), Symbol("F_M2")], [Symbol("F_V0"), Symbol("F_V1")])
    pt = pt012_def.create(Symbol("beh", FunctionType(REAL, [REAL])))
    print(pt.behaviour_formula.serialize())
'''