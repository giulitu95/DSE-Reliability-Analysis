from patterns.pattern import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.voter import Voter
from pysmt.shortcuts import *


class TmrV122Definition(PatternDefinition):
    """
    Definition for pattern TMR-V122
    """
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_f_atoms: list, voters_f_atoms: list):
        """
        Create a definition for pattern TMRV122
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voter_f_atom: fault atom associated to the voter
        """
        self._modules_f_atoms = modules_f_atoms
        assert len(modules_f_atoms) == 3, "[" + pt_name + "] pattern has 3 modules, a correct number of fault atoms"
        self._voters_f_atoms = voters_f_atoms
        assert len(voters_f_atoms) == 3, "[" + pt_name + "] pattern has 3 voters, a correct number of fault atoms"
        super(TmrV122Definition, self).__init__(comp_name, pt_name, comp_n_inputs, modules_f_atoms + voters_f_atoms, PatternType.TMR_V122)
        self._pt_name = pt_name

    def get_dummy_definition(self) -> 'TmrV122Definition':
        return TmrV122Definition("EMPTY", self.comp_n_inputs, [Symbol("EMPTY_F" + str(idx)) for idx in range(3)], [Symbol("EMPTY_F" + str(idx+3)) for idx in range(3)])

    def create(self, nominal_mod_beh) -> Pattern:
        return TmrV122(self._comp_name, self._pt_name, self._comp_n_inputs, self._modules_f_atoms, self._voters_f_atoms, nominal_mod_beh)

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



class TmrV122(Pattern):
    """
    Represent a pattern of type tmr-v122
    """
    n_f_atoms = 5
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_fault_atoms: list, voters_fault_atoms: list, nominal_mod_beh: Symbol):
        """
        Creata TMR-V122 pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param voter_fault_atoms: list of fault atoms associated to the voters
        :param nominal_mod_beh: nominal behavior of the modules
        """
        pattern_name = comp_name + "." + pt_name
        modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx], nominal_mod_beh) for idx in range(3)]                
        
        # The output of the modules are the inputs of the voters
        modules_out_ports = []
        for module in modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 3, "[" + pattern_name + "] The voters must have 3 inputs"
        voters = [Voter(pattern_name + ".V" + str(idx), voters_fault_atoms[idx], input_ports=modules_out_ports) for idx in range(2)]

        # Output1: output port of voter 1, Output2 and output 3: output port of voter 2  
        output_ports = []        
        output_ports.extend(voters[0].output_ports)
        output_ports.extend(voters[1].output_ports)
        output_ports.extend(voters[1].output_ports)
        assert len(output_ports) == 3, "[" + pattern_name + "] The pattern must have 3 outputs"                
        super(TmrV122, self).__init__(pattern_name, PatternType.TMR_V122, modules_fault_atoms + voters_fault_atoms, modules, output_ports)

        # Define behavior formula: And of subcomponents' behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in modules]
        # Voter
        subcomp_beh_formula.append([voter.behaviour_formula for voter in voters])
        self._behaviour_formula = And(subcomp_beh_formula)