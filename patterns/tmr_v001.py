from patterns.pattern import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.voter import Voter
from pysmt.shortcuts import *
from networkx.algorithms.centrality.degree_alg import out_degree_centrality


class TmrV001Definition(PatternDefinition):
    """
    Definition for pattern TMR-V001
    """
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_f_atoms: list, voter_f_atom: Symbol):
        """
        Create a definition for pattern TMRV001
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voter_f_atom: fault atom associated to the voter
        """
        self._modules_f_atoms = modules_f_atoms
        assert len(modules_f_atoms) == 3, "[" + pt_name + "] pattern has 3 modules, a correct number of fault atoms"
        self._voter_f_atom = voter_f_atom
        super(TmrV001Definition, self).__init__(comp_name, pt_name, comp_n_inputs, modules_f_atoms + [voter_f_atom], PatternType.TMR_V001)
        self._pt_name = pt_name

    def get_dummy_definition(self) -> 'TmrV001Definition':
        return TmrV001Definition("EMPTY", self.comp_n_inputs, [Symbol("EMPTY_F" + str(idx)) for idx in range(3)], Symbol("EMPTY_F3"))

    def create(self, nominal_mod_beh) -> Pattern:
        return TmrV001(self._comp_name, self._pt_name, self._comp_n_inputs, self._modules_f_atoms, self._voter_f_atom, nominal_mod_beh)

    @property
    def modules_f_atoms(self) -> list:
        """
        :return: list of fault atoms related to the modules of the patterns
        """
        return self._modules_f_atoms

    @property
    def voter_f_atom(self) -> Symbol:
        """
        :return: fault atom related to the voter of the pattern
        """
        return self._voter_f_atom



class TmrV001(Pattern):
    """
    Represent a pattern of type tmr-v001
    """
    n_f_atoms = 4
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_fault_atoms: list, voter_fault_atom: Symbol, nominal_mod_beh: Symbol):
        """
        Creata TMR-V001 pattern
        :param comp_name: name of the component to which the pattern has to be applied
        :param comp_n_inputs: number of inputs of the component to which the pattern has to be applied
        :param modules_fault_atoms: list of fault atoms associated to the 3 modules
        :param voter_fault_atom: fault atom associated to the voter
        :param nominal_mod_beh: nominal behavior of the modules
        """
        pattern_name = comp_name + "." + pt_name
        modules = [FaultyModule(pattern_name + ".M" + str(idx), comp_n_inputs, modules_fault_atoms[idx], nominal_mod_beh) for idx in range(3)]        
        
        # The output of the modules are the inputs of the voter
        modules_out_ports = []
        for module in modules:
            modules_out_ports.extend(module.output_ports)
        assert len(modules_out_ports) == 3, "[" + pattern_name + "] The voter must have 3 inputs"
        self._voter = Voter(pattern_name + ".V", voter_fault_atom, input_ports=modules_out_ports)
        
        # Output port of the pattern corresponds to the output ports of Module 1 and Module 2 and output port of the voter 
        output_ports = []        
        fan_outs=(module[0], module[1]) #0 0 
        output_ports.extend(fan_outs)
        output_ports.extend(self._voter.output_ports)   #1
        assert len(output_ports) == 3, "[" + pattern_name + "] The pattern must have 3 outputs"
        super(TmrV001, self).__init__(pattern_name, PatternType.TMR_V001, modules_fault_atoms + [voter_fault_atom], modules, output_ports)

        # Define behavior formula: And of subcomponents behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in modules]
        # Voter
        subcomp_beh_formula.append(self._voter.behaviour_formula)
        self._behaviour_formula = And(subcomp_beh_formula)

# Test - Example
if __name__ == "__main__":
    tmr = TmrV001("C1", "P1", 1, [Symbol("F0"), Symbol("F1"), Symbol("F2")], Symbol("F3"),  Symbol("Beh"))
    print(tmr.behaviour_formula.serialize())
