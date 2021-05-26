from patterns import PtType
from component import ComponentType, Component
from pysmt.shortcuts import *

class Csa:
    '''
    Class providing methods and attribute to compute the formula which represents the sequential composition of
    components Concretizer - Stage - Abstractor
    '''
    def __init__(self, comp_name: str, comp_n_inputs: int, pt_type: PtType, fault_atoms: list):
        '''
        Create a CSA
        :param comp_name: name of the component
        :param comp_n_inputs: number of inputs of the basic component
        :param pt_type: type of pattern
        :param fault_atoms: list of available fault atoms
        '''
        pass


class Concretizer(Component):
    """
    Class representing a Concretizer component
    """
    def __init__(self, name: str, comp_n_inputs: int, pattern_n_inputs: int,  input_ports: list = None, output_pattern_ports: list = None, output_comp_ports: list = None):
        """
        Create a concretizer component
        :param name: name of the concretizer
        :param comp_n_inputs: number of inputs of the nominal component
        :param pattern_n_inputs: number of inputs of the pattern
        :param input_ports: (otional) input ports
        :param output_ports: (optional) output ports
        """
        # Define input and output ports
        if input_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx)) for idx in range(pattern_n_inputs)]
        if output_comp_ports is None and output_pattern_ports is None:
            output_pattern_ports = [Symbol(name + ".o" + str(idx), REAL) for idx in range(pattern_n_inputs)]
            output_comp_ports = [Symbol(name + ".o" + str(idx), REAL) for idx in range(comp_n_inputs)]

        self._output_pattern_ports = output_pattern_ports
        self._output_comp_ports = output_comp_ports
        # First component output ports and then pattern's output ports
        super(Concretizer, self).__init__(name, ComponentType.CONCRETIZER, input_ports, output_comp_ports + output_pattern_ports)

        # TODO: check this:
        #  the number of pattern's inputs should be a multiple of the number of the component's inputs
        assert len(output_pattern_ports) % len(output_comp_ports) == 0, "[Concretizer] Incompatible number of pattern's inputs and component's inputs"
        # NOTICE! component's inputs and pattern's input have to have the same index!
        out_constraints = []
        for idx, patt_port in enumerate(self._output_pattern_ports):
            out_constraints.append(
                Iff(
                    self._input_ports[idx],
                    Equals(
                        patt_port,
                        self._output_comp_ports[idx % len(self._output_comp_ports)]
                    )
                )
            )
        self._behaviour_formula = And(out_constraints)


class Abstractor(Component):
    '''
    Class representing an Abstractor component
    '''
    def __init__(self, name: str, comp_n_outputs: int, pattern_n_inputs: int,  input_ports: list = None, output_pattern_ports: list = None, output_comp_ports: list = None):
        '''
        Crewate an abstractor
        :param name: abstractor's name
        :param n_inputs: number of abstractor's inputs
        '''
