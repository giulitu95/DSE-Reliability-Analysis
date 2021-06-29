#!/usr/bin/env python

from patterns import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.comparator import Comparator
from pysmt.shortcuts import *

__author__ = "Antonio Tierno"


class CmpDefinition(PatternDefinition):
    """
    Definition for pattern Comparator
    """
    def __init__(self, comp_name: str, comp_n_inputs: int, modules_f_atoms: list, comparator_f_atom: Symbol):
        """
        Create a definition for pattern CMP
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voter_f_atom: fault atom associated to the comparator
        """
        pt_type = PatternType.CMP
        self._modules_f_atoms = modules_f_atoms
        assert len(modules_f_atoms) == 2, "[" + pt_type.name + "] pattern has 2 modules, choose a correct number of fault atoms"
        self._comparator_f_atom = comparator_f_atom
        #assert len(comparator_f_atom) == 1, "[" + pt_type.name + "] pattern has 1 comparator, choose a correct number of fault atoms"
        super(CmpDefinition, self).__init__(comp_name, comp_n_inputs, modules_f_atoms + comparator_f_atom, PatternType.CMP)
        self._pt_name = pt_name


    def create(self, nominal_mod_beh) -> Pattern:
        return Cmp(self._comp_name, self._comp_n_inputs, self._modules_f_atoms, self._comparator_f_atom, nominal_mod_beh)

    @property
    def modules_f_atoms(self) -> list:
        """
        :return: list of fault atoms related to the modules of the patterns
        """
        return self._modules_f_atoms

    @property
    def comparator_f_atom(self) -> Symbol:
        """
        :return: fault atom related to the comparator of the pattern
        """
        return self._comparator_f_atom


class Cmp(Pattern):
    """
    Represent a pattern of type cmp
    """
    n_f_atoms = 3

    def __init__(self, comp_name: str, comp_n_inputs: int, modules_fault_atoms: list, comparator_fault_atom: Symbol):
        """
        Creata CMP pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param comparator_fault_atom: fault atom associated to the comparator
        :param nominal_mod_beh: nominal behavior of the modules
        """
        pattern_name = comp_name + "." + PatternType.CMP.name
        modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx], nominal_mod_beh) for idx in range(2)]

        # The output of the modules are the inputs of the comparator
        modules_out_ports = []
        for module in modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 2, "[" + pattern_name + "] Comparator must have 2 inputs"
        self._comparator = Comparator(pattern_name + ".C", comparator_fault_atom, input_ports=modules_out_ports)

        # Output of the pattern corresponds to the output ports of the comparator
        output_ports = self._comparator.output_ports
        #assert len(output_ports) == 1, "[" + pattern_name + "] The pattern must have 1 output"
        super(Cmp, self).__init__(pattern_name, PatternType.CMP, modules_fault_atoms + comparator_fault_atom, modules, output_ports)

        # Define behavior formula: And of subcomponents' behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in modules]
        # Comparator
        subcomp_beh_formula.extend(self._comparator.behavior_formula)
        self._behaviour_formula = And(subcomp_beh_formula)

