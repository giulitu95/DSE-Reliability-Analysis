from patterns.pattern import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.voter_v2 import Voter_v2 
from pysmt.shortcuts import *
from components import voter_v2

class XooY_3oo4_Definition(PatternDefinition):
    """
    Definition for pattern 3-o-o-4
    """
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_f_atoms: list, voter_f_atom: Symbol):
        """
        Create a definition for pattern 3-oo-4
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voter_f_atom: fault atom associated to the voter
        """
        self._modules_f_atoms = modules_f_atoms
        assert len(modules_f_atoms) == 4, "[" + pt_name + "] pattern has 3 modules, a correct number of fault atoms"
        self._voter_f_atom = voter_f_atom
        super(XooY_3oo4_Definition, self).__init__(comp_name, pt_name, comp_n_inputs, modules_f_atoms + [voter_f_atom], PatternType.XooY_3oo4)
        self._pt_name = pt_name

    def get_dummy_definition(self) -> 'TmrV123Definition':
        return XooY_3oo4_Definition("EMPTY", self.comp_n_inputs, [Symbol("EMPTY_F" + str(idx)) for idx in range(4)], Symbol("EMPTY_F4"))

    def create(self, nominal_mod_beh) -> Pattern:        
        return XooY_3oo4(self._comp_name, self._pt_name, self._comp_n_inputs, self._modules_f_atoms, self._voter_f_atom, nominal_mod_beh)

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
        return self._voter_f_atom



class XooY_3oo4(Pattern):
    """
    Represent a pattern of type 3-o-o-4
    """
    n_f_atoms = 6
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_fault_atoms: list, voter_fault_atom: Symbol, nominal_mod_beh: Symbol):
        """
        Create 3-o-o-4 pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 4 modules
        :param voter_fault_atom: fault atom associated to the voter
        :param nominal_mod_beh: nominal behavior of the modules
        """
        pattern_name = comp_name + "." + pt_name
        modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx], nominal_mod_beh) for idx in range(4)]                
        
        # The output of the modules are the inputs of the voters
        modules_out_ports = []
        for module in modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 4, "[" + pattern_name + "] The voters must have 4 inputs"
        self._voter = Voter_v2(pattern_name + ".V", voter_fault_atom, input_ports=modules_out_ports)

        # Output port of the pattern corresponds to the output port of the voter
        output_ports = self._voter.output_ports
        super(XooY_3oo4, self).__init__(pattern_name, PatternType.XooY_3oo4, modules_fault_atoms + [voter_fault_atom], modules, output_ports)
                
        # Define behavior formula: And of subcomponents' behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in modules]
        # Voter
        subcomp_beh_formula.append(self._voter.behaviour_formula)
        self._behaviour_formula = And(subcomp_beh_formula)
