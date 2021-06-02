from patterns.pattern import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.comparator import Comparator
from pysmt.shortcuts import *


class Dpx_hm_Definition(PatternDefinition):
    """
    Definition for pattern TMR-V123
    """
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_f_atoms: list, comparator_f_atom: Symbol):
        """
        Create a definition for pattern TMRV123
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param comparator_f_atom: fault atom associated to the comparator
        """
        self._modules_f_atoms = modules_f_atoms
        assert len(modules_f_atoms) == 2, "[" + pt_name + "] pattern has 2 modules, a correct number of fault atoms"
        self._comparator_f_atom = comparator_f_atom        
        super(Dpx_hm_Definition, self).__init__(comp_name, pt_name, comp_n_inputs, modules_f_atoms + [comparator_f_atom], PatternType.DPX_HM)
        self._pt_name = pt_name

    def get_dummy_definition(self) -> 'Dpx_hm_Definition':
        return Dpx_hm_Definition("EMPTY", self.comp_n_inputs, [Symbol("EMPTY_F" + str(idx)) for idx in range(2)], Symbol("EMPTY_F2"))

    def create(self, nominal_mod_beh) -> Pattern:
        return Dpx_hm(self._comp_name, self._pt_name, self._comp_n_inputs, self._modules_f_atoms, self._comparator_f_atom, nominal_mod_beh)

    @property
    def modules_f_atoms(self) -> list:
        """
        :return: list of fault atoms related to the modules of the patterns
        """
        return self._modules_f_atoms

    @property
    def comparator_f_atom(self) -> list:
        """
        :return: fault atom related to the voter of the pattern
        """
        return self._comparator_f_atom
    
class Dpx_hm(Pattern):
    """
    Represent a pattern of type homogeneous duplex
    """
    n_f_atoms = 3
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_fault_atoms: list, comparator_fault_atom: Symbol, nominal_mod_beh: Symbol):    
        """
        Create DPX pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param comparator_fault_atom: fault atom associated to the voter
        """
        pattern_name = comp_name + "." + pt_name
        modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx], nominal_mod_beh) for idx in range(2)]        
        
        # The output of the modules are the inputs of the comparator
        modules_out_ports = []        
        for module in self._modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 2, "Comparator must have 2 inputs"
        self._comparator = Comparator(pattern_name + ".C", comparator_fault_atom, input_ports=modules_out_ports)
        
        # Output port of the pattern corresponds to the output port of the comparator
        output_ports = self._comparator.output_ports
        super(Dpx_hm, self).__init__(pattern_name, PatternType.DPX_HM, modules_fault_atoms + [comparator_fault_atom], modules, output_ports)
        
        # Define behavior formula: And of subcomponents behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in self._modules]
        # Comparator
        subcomp_beh_formula.append(self._comparator.behaviour_formula)
        self._behaviour_formula = And(subcomp_beh_formula)
 
# Test - Example
if __name__ == "__main__":
    dpx = Dpx_hm("C1", "P1", 1, [Symbol("F0"), Symbol("F1")], Symbol("F2"),  Symbol("Beh"))
    print(dpx.behaviour_formula.serialize())
    