from components.component import Component, ComponentType
from pysmt.shortcuts import *


class FaultyModule(Component):

    def __init__(self, name: str, n_in_ports: int, fault_atom: Symbol, nominal_beh: Symbol,  input_ports: list = None, output_port: Symbol = None):
        """
        Create a faulty module, if input_ports and outputs_ports symbols are not specified, then the constructor creates them
        :param name: module's name
        :param n_in_ports: number of module's inputs
        """
        self._fault_atom = fault_atom

        # Define input and output ports
        if input_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx), REAL) for idx in range(n_in_ports)]
        else:
            assert len(input_ports) == n_in_ports, "The number of specified input ports does not match with n_in_ports"
        if output_port is None:
            output_port = Symbol(name + ".o0", REAL)

        super(FaultyModule, self).__init__(name, ComponentType.VOTER, input_ports, [output_port], fault_atoms=[fault_atom])

        self._behaviour_formula = Implies(
            Not(self._fault_atom),
            Equals(
                self._output_ports[0],
                Function(nominal_beh, self._input_ports)
            )
        )


class NominalModule(Component):
    def __init__(self, name: str, n_in_ports: int, input_ports: list = None, output_port: Symbol = None):
        """
        Create a nominal module, if input_ports and outputs_ports symbols are not specified, then the constructor creates them
        :param name: module's name
        :param n_in_ports: number of module's inputs
        """
        # Define input and output ports
        if input_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx), REAL) for idx in range(n_in_ports)]
        else:
            assert len(input_ports) == n_in_ports, "The number of specified input ports does not match with n_in_ports"
        if output_port is None:
            output_port = Symbol(name + ".o0", REAL)

        super(NominalModule, self).__init__(name, ComponentType.VOTER, input_ports, [output_port])

        out_behaviour_func = Symbol(name + ".beh", FunctionType(REAL, [REAL] * len(input_ports)))
        self._nominal_beh = out_behaviour_func
        self._behaviour_formula = Equals(
            self._output_ports[0],
            Function(out_behaviour_func, self._input_ports)
        )

    @property
    def nominal_beh (self):
        return self._nominal_beh