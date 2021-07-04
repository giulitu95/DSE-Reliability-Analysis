#!/usr/bin/env python

from patterns import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.voter import Voter
from pysmt.shortcuts import *

__author__ = "Antonio Tierno"


class TmrV101Definition(PatternDefinition):
    """
    Definition for pattern TMR-V101
    """
    def __init__(self, comp_name: str, comp_n_inputs: int, modules_f_atoms: list, voters_f_atoms: list):
        """
        Create a definition for pattern TMRV101
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voters_f_atomsf_atom: fault atom associated to the voter
        """
        self._modules_f_atoms = modules_f_atoms
        self._voters_f_atoms = voters_f_atoms
        super(TmrV101Definition, self).__init__(comp_name,  comp_n_inputs, modules_f_atoms + voters_f_atoms, PatternType.TMR_V101)
        pt_name = self._pt_type.name
        assert len(modules_f_atoms) == 3, "[" + pt_name + "] pattern has 3 modules, choose a correct number of fault atoms"
        self._pt_name = pt_name

    def create(self, nominal_mod_beh) -> Pattern:
        return TmrV101(self._comp_name, self._comp_n_inputs, self._modules_f_atoms, self._voters_f_atoms, nominal_mod_beh)

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


class TmrV101(Pattern):
    """
    Represent a pattern of type tmr-v101
    """
    n_f_atoms = 5

    def __init__(self, comp_name: str, comp_n_inputs: int, modules_fault_atoms: list, voters_fault_atoms: list, nominal_mod_beh: Symbol):
        """
        Creata TMR-V010 pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param voters_fault_atoms: fault atom associated to the voters
        :param nominal_mod_beh: nominal behaviour of the modules
        """
        pattern_name = comp_name + "." + PatternType.TMR_V101.name
        modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx], nominal_mod_beh) for idx in range(3)]

        # The output of the modules are the inputs of the voter
        modules_out_ports = []
        for module in modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 3, "[" + pattern_name + "] The voter must have 3 inputs"
        voters = [Voter(pattern_name + ".V" + str(idx), voters_fault_atoms[idx], input_ports=modules_out_ports) for idx
                  in range(2)]

        # Output port of the pattern corresponds to the output ports of the voter, of Module 2, of the voter
        output_ports = modules_out_ports
        output_ports[0] = voters[0].output_ports[0]
        output_ports[2] = voters[1].output_ports[0]
        assert len(output_ports) == 3, "[" + pattern_name + "] The pattern must have 3 outputs"
        super(TmrV101, self).__init__(pattern_name, PatternType.TMR_V101, modules_fault_atoms + voters_fault_atoms,
                                      modules, output_ports)

        # Define behaviour formula: And of subcomponents behaviours
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in modules]
        # Voter
        subcomp_beh_formula.extend([voter.behaviour_formula for voter in voters])
        self._behaviour_formula = And(subcomp_beh_formula)



'''# Test - Example
if __name__ == "__main__":
    nominal_beh = Symbol("nom-beh", FunctionType(REAL, [REAL]))
    tmr = TmrV101("C1", 1, [Symbol("F_M0"), Symbol("F_M1"), Symbol("F_M2")], [Symbol("F_V0"), Symbol("F_V1")], nominal_beh)
    print(tmr.behaviour_formula.serialize())
    print(tmr.output_ports)'''
