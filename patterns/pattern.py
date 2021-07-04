#!/usr/bin/env python

from components.component import Component, ComponentType
from enum import Enum
import abc

__author__ = "Giuliano Turri, Antonio Tierno"


class PatternType(Enum):
    """
    Enum which determines the type of pattern (e.g. DPX, TMR_V111, TRM_V123...)
    """
    PLAIN = 1
    CMP = 2
    TMR_V111 = 3
    TMR_V001 = 4
    TMR_V010 = 5
    TMR_V100 = 6
    TMR_V011 = 7
    TMR_V101 = 8
    TMR_V110 = 9
    TMR_V122 = 10
    TMR_V112 = 11
    TMR_V120 = 12
    TMR_V102 = 13
    TMR_V012 = 14
    TMR_V123 = 15
    Xooy_3oo4 = 16
    # Add more patterns here...


class PatternDefinition:
    """
    Description of a pattern
    """
    def __init__(self, comp_name: str, comp_n_inputs: int, f_atoms: list, pt_type: PatternType):
        """
        Create the description of a particular pattern
        :param comp_name: name of the component for which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component for which the pattern has to be applied
        :param f_atoms: fault_atoms of the pattern
        :param pt_type: type of pattern
        """
        self._atoms = f_atoms
        self._pt_type = pt_type
        self._comp_name = comp_name
        self._comp_n_inputs = comp_n_inputs

    @abc.abstractmethod
    def create(self, nominal_mod_beh) -> 'Pattern':
        """
        Creates an instance of the pattern having the current definition
        :param nominal_mod_beh: the nominal behaviour of the component
        :return: an instance of the pattern
        """
        pass

    @property
    def f_atoms(self) -> list:
        """
        :return: the list of fault_atoms for the pattern
        """
        return self._atoms

    @property
    def pt_type(self) -> PatternType:
        """
        :return: type of pattern
        """
        return self._pt_type

    @property
    def comp_name(self) -> str:
        """
        :return: the name of the component
        """
        return self._comp_name

    @property
    def comp_n_inputs(self) -> int:
        """
        :return: number of inputs of the components
        """
        return self._comp_n_inputs


class Pattern(Component):
    """
    Class representing a general pattern
    """
    def __init__(self, name: str, pattern_type: PatternType, fault_atoms: list, modules: list, output_ports: list):
        """
        Create a generic pattern
        :param name: name of the instance of the pattern
        :param pattern_type: type of pattern
        :param fault_atoms: list of available fault atoms for that pattern
        :param input_ports: list of symbols corresponding to the input ports
        :param output_ports: list of symbols corresponding to the output ports
        """
        input_ports = []
        for module in modules:
            input_ports.extend(module.input_ports)
        self._modules = modules
        super(Pattern, self).__init__(name, ComponentType.PATTERN, input_ports, output_ports, fault_atoms=fault_atoms)
        self._pattern_type = pattern_type

    @property
    def modules(self):
        return self._modules
