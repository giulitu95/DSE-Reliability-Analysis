from components.component import Component, ComponentType
from pysmt.shortcuts import *
from utils import majority_element

class Voter_v2(Component):    
    def __init__(self, name: str, fault_atom: Symbol, input_ports: list = None, output_port: Symbol = None):
        """
        Create a voter, if input_ports and outputs_ports symbols are not specified, then the constructor creates them
        :param name: name of voter
        :param faulty_atom: symbol used to indicate whether the voter is faulty
        :param input_ports: list of symbols corresponding to the voter's input ports
        :param outpu_port: symbol corresponding to the voter's output port
        """
        self._fault_atom = fault_atom
        
        #number of inputs
        n_inp = len(input_ports)
        
        # Define input and output ports
        if input_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx), REAL) for idx in range(n_inp)]
        else:
            assert len(input_ports) == n_inp, "Voter can only accept " + n_inp + " input ports"
        if output_port is None:
            output_port = [Symbol(name + ".o0", REAL)]

        super(Voter_v2, self).__init__(name, ComponentType.VOTER, input_ports, output_port, fault_atoms=[fault_atom])
        
        # Define nominal behavior        
        idx = majority_element(input_ports)
        nom_behaviour = Equals(
            self._output_ports[0],
            self._input_ports[idx]
            )        
            
        # if faulty atom is false, then the behavior is nominal
        self._behaviour_formula = Implies(
                Not(self._fault_atom),
                nom_behaviour
            )
        


# Test - Example
if __name__ == "__main__":
    example_voter = Voter_v2("C1-TMR_V11.V", Symbol("F"), [Symbol("I0", REAL), Symbol("I1", REAL), Symbol("I2", REAL)])
    print(example_voter.behaviour_formula.serialize())
    
    example_voter2 = Voter_v2("C1-TMR_V11.V", Symbol("F"), [Symbol("I0", REAL), Symbol("I1", REAL), Symbol("I1", REAL), Symbol("I2", REAL) ])
    print(example_voter2.behaviour_formula.serialize())