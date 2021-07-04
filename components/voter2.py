#!/usr/bin/env python

from components.component import Component, ComponentType
from pysmt.shortcuts import *

__author__ = "Antonio Tierno"


class Voter2(Component):

    def __init__(self, name: str, fault_atom: Symbol, input_ports: list = None, output_port: Symbol = None):
        """
        Create a voter, if input_ports and outputs_ports symbols are not specified, then the constructor creates them
        :param name: name of voter
        :param faulty_atom: symbol used to indicate whether the voter is faulty
        :param input_ports: list of symbols corresponding to the voter's input ports
        :param outpu_ports: lsit of symbols corresponding to the voter's output ports
        """
        self._fault_atom = fault_atom
        # Define input and output ports
        if input_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx), REAL) for idx in range(4)]
        else:
            assert len(input_ports) == 4, "Voter can only accept 4 input ports"
        if output_port is None:
            output_port = [Symbol(name + ".o0", REAL)]

        super(Voter2, self).__init__(name, ComponentType.VOTER, input_ports, output_port, fault_atoms=[fault_atom])
        # Define nominal behaviour
        nom_behaviour = And(
            Ite(
                Or(
                    And(
                        Equals(
                            self._input_ports[0],
                            self._input_ports[1]
                            ),
                        Equals(
                            self._input_ports[0],
                            self._input_ports[2]
                        )
                    ),
                    And(
                        Equals(
                            self._input_ports[0],
                            self._input_ports[1]
                        ),
                        Equals(
                            self._input_ports[0],
                            self._input_ports[3]
                        )
                    ),
                    And(
                        Equals(
                            self._input_ports[0],
                            self._input_ports[2]
                        ),
                        Equals(
                            self._input_ports[0],
                            self._input_ports[3]
                        )
                    )
                ),
                Equals(
                    self._output_ports[0],
                    self._input_ports[0]
                ),
                Equals(
                    self._output_ports[0],
                    self._input_ports[1]
                )
            )
        )
        # if faulty atom is false, then the behaviour is nominal
        self._behaviour_formula = Implies(
                Not(self._fault_atom),
                nom_behaviour
            )


# Test - Example
if __name__ == "__main__":
    v = Voter2("C1-3oo4.V", Symbol("F"), [Symbol("I0", REAL), Symbol("I1", REAL), Symbol("I2", REAL), Symbol("I3", REAL)])
    print(v.behaviour_formula.serialize())
