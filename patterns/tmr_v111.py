from patterns.pattern import Pattern, PatternType
from components.module import FaultyModule
from components.voter import Voter
from pysmt.shortcuts import *


class TmrV111(Pattern):
    """
    Represent a pattern of type tmr-v111
    """
    def __init__(self, comp_name: str, comp_n_inputs: int, modules_fault_atoms: list, voter_fault_atom: Symbol):
        """
        Creata TMR-V111 pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param voter_fault_atom: fault atom associated to the voter
        """
        pattern_name = comp_name + ".TMR_V111"
        self._modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx]) for idx in range(3)]
        modules_out_ports = []
        # The output of the modules are the inputs of the voter
        for module in self._modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 3, "[TmrV11] The voter must have 3 inputs"
        self._voter = Voter(pattern_name + ".V", voter_fault_atom, input_ports=modules_out_ports)
        # Input ports of the pattern correspond to the input ports of the modules
        input_ports = []
        for module in self._modules: input_ports.extend(module.input_ports)
        # Output port of the pattern corresponds to the output port of the voter
        output_ports = self._voter.output_ports
        super(TmrV111, self).__init__(pattern_name, PatternType.TMR_V111, modules_fault_atoms + [voter_fault_atom], input_ports, output_ports)

        # Define behaviour formula: And of subcomponents behaviours
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in self._modules]
        # Voter
        subcomp_beh_formula.append(self._voter.behaviour_formula)
        self._behaviour_formula = And(subcomp_beh_formula)


'''
# Test - Example
if __name__ == "__main__":
    tmr = TmrV111("C1", 1, [Symbol("F0"), Symbol("F1"), Symbol("F2")], Symbol("F3"))
    print(tmr.behaviour_formula.serialize())

    # Output
    # (((! F0) -> (C1.TMR_V111.M0.o0 = C1.TMR_V111.M0.beh(C1.TMR_V111.M0.i0))) & 
    # ((! F1) -> (C1.TMR_V111.M1.o0 = C1.TMR_V111.M1.beh(C1.TMR_V111.M1.i0))) & 
    # ((! F2) -> (C1.TMR_V111.M2.o0 = C1.TMR_V111.M2.beh(C1.TMR_V111.M2.i0))) & 
    # ((! F3) -> (((C1.TMR_V111.M0.o0 = C1.TMR_V111.M1.o0) | (C1.TMR_V111.M0.o0 = C1.TMR_V111.M2.o0)) ? (C1.TMR_V111.V.o0 = C1.TMR_V111.M0.o0) : ((C1.TMR_V111.M1.o0 = C1.TMR_V111.M2.o0) -> (C1.TMR_V111.V.o0 = C1.TMR_V111.M1.o0)))))
'''