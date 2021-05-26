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
        :param output_pattern_ports: (optional) output ports related to the pattern's inputs
        :param output_comp_ports: (optional) output ports related to the component's inputs
        """
        # Define input and output ports
        if input_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx)) for idx in range(pattern_n_inputs)]
        if output_comp_ports is None or output_pattern_ports is None:
            output_ports = [Symbol(name + ".o" + str(idx), REAL) for idx in range(comp_n_inputs + pattern_n_inputs)]
            output_pattern_ports = output_ports[:comp_n_inputs]
            output_comp_ports = output_ports[:comp_n_inputs]
        else:
            output_ports = output_comp_ports + output_pattern_ports
        self._output_pattern_ports = output_pattern_ports
        self._output_comp_ports = output_comp_ports
        # First component output ports and then pattern's output ports
        super(Concretizer, self).__init__(name, ComponentType.CONCRETIZER, input_ports, output_ports)

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
    def __init__(self, name: str, pattern_n_inputs: int,  output_ports: list = None, input_pattern_ports: list = None, input_comp_port: Symbol = None):
        """
        Create an Abstractor
        :param name: name of the abstractor
        :param pattern_n_inputs: number of inputs corresponding to the pattern's output
        :param output_ports: (optional) list of output ports
        :param input_pattern_ports: (optional) list of input ports corresponding to the outputs of the patter
        :param input_comp_port: (optional)  input portscorresponding to the output of the nominal component
        """
        # Define input and output ports
        if output_ports is None:
            output_ports = [Symbol(name + ".o" + str(idx)) for idx in range(pattern_n_inputs)]
        if input_comp_port is None or input_pattern_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx), REAL) for idx in range(1 + pattern_n_inputs)]
            input_pattern_ports = input_ports[1:]
            input_comp_port = input_ports[:1]
        else:
            input_ports = input_comp_port + input_pattern_ports
        self._input_pattern_ports = input_pattern_ports
        self._input_comp_port = input_comp_port
        super(Abstractor, self).__init__(name,ComponentType.ABSTRACTOR, input_ports, output_ports)

        # The number of pattern's input port and abstractor's output ports have to be the same
        assert len(input_pattern_ports) == len(output_ports), "[Abstractor] number of pattern's outputs and abstractor's outputs have to be the same"
        # Define behaviour
        out_constraints = []
        for idx, patt_port in enumerate(self._input_pattern_ports):
            out_constraints.append(
                Iff(
                    Equals(
                        patt_port,
                        self._input_comp_port
                    ),
                    self._output_ports[idx]
                )
            )
        self._behaviour_formula = And(out_constraints)
