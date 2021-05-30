from patterns.pattern import Pattern, PatternType, PatternDefinition
from components.module import FaultyModule
from components.voter import Voter
from pysmt.shortcuts import *


class TmrV111Definition(PatternDefinition):
    """
    Definition for pattern TMR-V111
    """
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_f_atoms: list, voter_f_atom: Symbol):
        """
        Create a definition for pattern TMRV111
        :param comp_name: name of the component
        :param comp_n_inputs: number of component's inputs
        :param modules_f_atoms: list of fault atoms of the pattern
        :param voter_f_atom: fault atom associated to the voter
        """
        self._modules_f_atoms = modules_f_atoms
        assert len(modules_f_atoms) == 3, "[" + pt_name + "] pattern has 3 modules, a correct number of fault atoms"
        self._voter_f_atom = voter_f_atom
        super(TmrV111Definition, self).__init__(comp_name, pt_name, comp_n_inputs, modules_f_atoms + [voter_f_atom], PatternType.TMR_V111)
        self._pt_name = pt_name

    def get_dummy_definition(self) -> 'TmrV111Definition':
        return TmrV111Definition("EMPTY", self.comp_n_inputs, [Symbol("EMPTY_F" + str(idx)) for idx in range(3)], Symbol("EMPTY_F3"))

    def create(self, nominal_mod_beh) -> Pattern:
        return TmrV111(self._comp_name, self._pt_name, self._comp_n_inputs, self._modules_f_atoms, self._voter_f_atom, nominal_mod_beh)

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



class TmrV111(Pattern):
    """
    Represent a pattern of type tmr-v111
    """
    n_f_atoms = 4
    def __init__(self, comp_name: str, pt_name: str, comp_n_inputs: int, modules_fault_atoms: list, voter_fault_atom: Symbol, nominal_mod_beh: Symbol):
        """
        Creata TMR-V111 pattern
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
        
        # Output port of the pattern corresponds to the output port of the voter
        output_ports = self._voter.output_ports
        super(TmrV111, self).__init__(pattern_name, PatternType.TMR_V111, modules_fault_atoms + [voter_fault_atom], modules, output_ports)

        # Define behavior formula: And of subcomponents behaviors
        # Modules
        subcomp_beh_formula = [module.behaviour_formula for module in modules]
        # Voter
        subcomp_beh_formula.append(self._voter.behaviour_formula)
        self._behaviour_formula = And(subcomp_beh_formula)



# Test - Example
if __name__ == "__main__":
    tmr = TmrV111("C1", "P1", 3, [Symbol("F0"), Symbol("F1"), Symbol("F2")], Symbol("F3"),  Symbol("Beh"))
    print(tmr.behaviour_formula.serialize())
'''
    # Output
    # (((! F0) -> (C1.TMR_V111.M0.o0 = C1.TMR_V111.M0.beh(C1.TMR_V111.M0.i0))) & 
    # ((! F1) -> (C1.TMR_V111.M1.o0 = C1.TMR_V111.M1.beh(C1.TMR_V111.M1.i0))) & 
    # ((! F2) -> (C1.TMR_V111.M2.o0 = C1.TMR_V111.M2.beh(C1.TMR_V111.M2.i0))) & 
    # ((! F3) -> (((C1.TMR_V111.M0.o0 = C1.TMR_V111.M1.o0) | (C1.TMR_V111.M0.o0 = C1.TMR_V111.M2.o0)) ? (C1.TMR_V111.V.o0 = C1.TMR_V111.M0.o0) : ((C1.TMR_V111.M1.o0 = C1.TMR_V111.M2.o0) -> (C1.TMR_V111.V.o0 = C1.TMR_V111.M1.o0)))))
'''