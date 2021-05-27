from component import Component, ComponentType
from module import NominalModule
from patterns import PatternType
from pysmt.shortcuts import *
from patterns.tmr_v111 import TmrV111


class Stage(Component):

    def __init__(self, comp_name: str, comp_n_inputs: int, pt_type: PatternType, fault_atoms: list):
        """
        Create a Stage given a component and a pattern
        :param comp_name: name of the component
        :param comp_n_inputs: number of inputs of the basic component
        :param pt_type: type of pattern
        :param fault_atoms: list of available fault atoms
        """
        self._nominal_module = NominalModule(comp_name + "_nom", comp_n_inputs)
        if pt_type == PatternType.TMR_V111:
            assert len(fault_atoms) >= 4, "[Stage] Not enough available fault atoms for a tmr_v111"
            self._pattern = TmrV111(comp_name, comp_n_inputs, fault_atoms[:3], fault_atoms[3], self._nominal_module.nominal_beh)
        else:
            NotImplementedError()

        # Define input and output ports
        input_ports = self._pattern.input_ports + self._nominal_module.input_ports
        output_ports = self._pattern.output_ports + self._nominal_module.output_ports

        super(Stage, self).__init__("[" + comp_name + "-" + pt_type.name + "].stage", ComponentType.STAGE, input_ports, output_ports, fault_atoms=self._pattern.fault_atoms)

        # Define behaviour formula: it corresponds to the behaviour of the pattern and the behaviour of the nominal module
        self._behaviour_formula = And(
            self._pattern.behaviour_formula,
            self._nominal_module.behaviour_formula
        )

    @property
    def pattern(self):
        """
        Pattern's getter
        :return: the pattern of the stage
        """
        return self._pattern

    @property
    def nominal_module(self):
        """
        nominal_modules's getter
        :return:  the nominal module of the stage
        """
        return self._nominal_module


# Test - Example
if __name__ == "__main__":
    st = Stage("C1", 1, PatternType.TMR_V111, [Symbol("F0"), Symbol("F1"), Symbol("F2"), Symbol("F3")])
    print(st.behaviour_formula.serialize())
    
    # Output
    # ((((! F0) -> (C1.TMR_V111.M0.o0 = C1_nom.beh(C1.TMR_V111.M0.i0))) &
    # ((! F1) -> (C1.TMR_V111.M1.o0 = C1_nom.beh(C1.TMR_V111.M1.i0))) &
    # ((! F2) -> (C1.TMR_V111.M2.o0 = C1_nom.beh(C1.TMR_V111.M2.i0))) &
    # ((! F3) -> (((C1.TMR_V111.M0.o0 = C1.TMR_V111.M1.o0) | (C1.TMR_V111.M0.o0 = C1.TMR_V111.M2.o0)) ? (C1.TMR_V111.V.o0 = C1.TMR_V111.M0.o0) : ((C1.TMR_V111.M1.o0 = C1.TMR_V111.M2.o0) -> (C1.TMR_V111.V.o0 = C1.TMR_V111.M1.o0))))) &
    # (C1_nom.o0 = C1_nom.beh(C1_nom.i0)))
