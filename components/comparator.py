from components.component import Component, ComponentType
from pysmt.shortcuts import *


class Comparator(Component):    
    def __init__(self, name: str, fault_atom: Symbol, input_ports: list = None, output_port: Symbol = None):
        """
        Create a comparator, if input_ports and outputs_ports symbols are not specified, then the constructor creates them
        :param name: name of comparator
        :param faulty_atom: symbol used to indicate whether the comparator is faulty
        :param input_ports: list of symbols corresponding to the comparator's input ports
        :param outpu_ports: list of symbols corresponding to the comparator's output ports
        """
        self._fault_atom = fault_atom
        # Define input and output ports
        if input_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx), REAL) for idx in range(2)]
        else:
            assert len(input_ports) == 2, "Comparator accepts 2 input ports"
        if output_port is None:
            output_port = [Symbol(name + ".o0", REAL)]

        super(Comparator, self).__init__(name, ComponentType.COMPARATOR, input_ports, output_port, fault_atoms=[fault_atom])
        # Define nominal behavior
        nom_behaviour = Equals(self._output_ports[0], self._input_ports[0])
                
        # if faulty atom is false, then the behavior is nominal
        self._behaviour_formula = Implies(
                Not(self._fault_atom),
                nom_behaviour
            )

'''
# Test - Example
if __name__ == "__main__":
    CMP1 = Comparator("C1-DPX_hm.C", Symbol("F"))
    print(CMP1.behaviour_formula.serialize())

    CMP2 = Comparator("C1-DPX_hm.C", Symbol("F"), [Symbol("I0", REAL), Symbol("I1", REAL)])
    print(CMP2.behaviour_formula.serialize())
'''