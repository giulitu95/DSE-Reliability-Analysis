from components.component import Component, ComponentType
from components.module import NominalModule
from patterns import PatternType, PatternDefinition
from pysmt.shortcuts import *
from patterns.tmr_v111 import TmrV111, TmrV111Definition
from typing import NamedTuple


class Stage(Component):
    def __init__(self, pt_definition: PatternDefinition):
        """
        Given a pattern definition, create a stage
        :param pt_definition: the definition of a pattern
        """
        self._nominal_module = NominalModule(pt_definition.comp_name + "_nom", pt_definition.comp_n_inputs)
        self._pattern = pt_definition.create(self._nominal_module.nominal_beh)

        # Define input and output ports
        input_ports = self._pattern.input_ports + self._nominal_module.input_ports
        output_ports = self._pattern.output_ports + self._nominal_module.output_ports

        super(Stage, self).__init__("[" + self._pattern.name + "].stage", ComponentType.STAGE, input_ports, output_ports, fault_atoms=self._pattern.fault_atoms)

        # Define behaviour formula: it corresponds to the behaviour of the pattern and the behaviour of the nominal module
        self._behaviour_formula = And(
            self._pattern.behaviour_formula,
            self._nominal_module.behaviour_formula
        )

    @property
    def pattern(self):
        """
        :return: the pattern of the stage
        """
        return self._pattern

    @property
    def nominal_module(self):
        """
        :return:  the nominal module of the stage
        """
        return self._nominal_module