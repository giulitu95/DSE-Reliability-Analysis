from components.component import Component, ComponentType
from pysmt.shortcuts import *


class Module(Component):

    def __init__(self, name: str, n_in_ports: int, fault_atom: Symbol, input_ports: list = None, output_port: Symbol = None):
        """
        Create a module, if input_ports and outputs_ports symbols are not specified, then the constructor creates them
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

        super(Module, self).__init__(name, ComponentType.VOTER, input_ports, [output_port])

        out_behaviour_func = Symbol(name + ".beh", FunctionType(REAL, [REAL] * len(input_ports)))
        out_constraint = Equals(
            self._output_ports[0],
            Function(out_behaviour_func, self._input_ports)
        )
        self._behaviour_formula = Implies(
            Not(self._fault_atom),
            out_constraint
        )

'''
# Test - Example
if __name__ == "__main__":
    m1 = Module("C1-TMR_V11.M1", 2, Symbol("F"))
    print(m1.behaviour_formula.serialize())

    m2 = Module("C1-TMR_V11.M1", 2, Symbol("F"), input_ports=[Symbol("i0", REAL), Symbol("i1", REAL)], output_port=Symbol("o0", REAL))
    print(m2.behaviour_formula.serialize())
'''