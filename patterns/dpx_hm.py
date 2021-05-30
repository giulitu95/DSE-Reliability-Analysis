from patterns.pattern import Pattern, PatternType
from components.module import FaultyModule
from components.voter import Voter
from pysmt.shortcuts import *
from components.comparator import Comparator

class Dpx_hm(Pattern):
    """
    Represent a pattern of type homogeneous duplex
    """
    def __init__(self, comp_name: str, comp_n_inputs: int, modules_fault_atoms: list, comparator_fault_atom: Symbol):
        """
        Create DPX pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param voter_fault_atom: fault atom associated to the voter
        """
        pattern_name = comp_name + ".Hm_DPX"
        self._modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx]) for idx in range(2)]
        modules_out_ports = []
        # The output of the modules are the inputs of the voter
        for module in self._modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 2, "Comparator must have 2 inputs"
        self._comparator = Comparator(pattern_name + ".C", comparator_fault_atom, input_ports=modules_out_ports)
        # Input ports of the pattern correspond to the input ports of the modules
        input_ports = []
        for module in self._modules: input_ports.extend(module.input_ports)
        # Output port of the pattern corresponds to the output port of the voter
        output_ports = self._comparator.output_ports
        super(Dpx_hm, self).__init__(pattern_name, PatternType.DPX_HM, modules_fault_atoms + [comparator_fault_atom], input_ports, output_ports)

        # Define behavior formula: And of subcomponents behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in self._modules]
        # Comparator
        subcomp_beh_formula.append(self._comparator.behaviour_formula)
        self._behaviour_formula = And(subcomp_beh_formula)

