from patterns import PatternType
from component import ComponentType, Component
from stage import Stage
from pysmt.shortcuts import *
import os
import mathsat
from pysmt.parsing import parse


class Csa(Component):
    '''
    Class providing methods and attribute to compute the formula which represents the sequential composition of
    components Concretizer - Stage - Abstractor
    '''

    def __init__(self, comp_name: str, comp_n_inputs: int, pt_type: PatternType, fault_atoms: list):
        '''
        Create a CSA, check if the formula is in cache, otherwise create it
        :param comp_name: name of the component
        :param comp_n_inputs: number of inputs of the basic component
        :param pt_type: type of pattern
        :param fault_atoms: list of available fault atoms
        '''
        self._comp_name = comp_name
        self._comp_n_inputs = comp_n_inputs
        self._pt_type = pt_type
        self._stage = Stage(comp_name, comp_n_inputs, pt_type, fault_atoms)
        # We can also delete this, this is needed only in order to compyte the behaviour formula which actually we don't need
        self._concretizer = Concretizer("[" + comp_name + "-" + pt_type.name + "].concr",
                                        comp_n_inputs, len(self._stage.pattern.input_ports),
                                        input_comp_ports=self._stage.nominal_module.input_ports,
                                        input_pattern_ports=self._stage.pattern.input_ports
                                        )
        self._abstractor = Abstractor("[" + comp_name + "-" + pt_type.name + "].abstr",
                                      len(self._stage.pattern.output_ports),
                                      output_pattern_ports=self._stage.pattern.output_ports,
                                      output_comp_port=self._stage.nominal_module.output_ports
                                      )

        super(Csa, self).__init__("[" + comp_name + "-" + pt_type.name + "].csa",
                                  ComponentType.CSA, self._concretizer.input_ports,
                                  self._abstractor.output_ports,
                                  fault_atoms=self._stage.fault_atoms
                                  )
        self._behaviour_formula = And(
            [self._stage.behaviour_formula, self._concretizer.behaviour_formula, self._abstractor.behaviour_formula])

    def get_qe_formula(self):
        file_name = os.path.join('../csa-cache/', self._pt_type.name + "_" + str(self._comp_n_inputs) + ".f")
        dummy_comp_name = "EMPTY"
        if not os.path.exists(file_name):
            # Create a generic csa and save it in cache
            fault_atoms = [Symbol("EMPTY_F" + str(idx)) for idx in range(len(self._fault_atoms))]
            stage = Stage(dummy_comp_name, self._comp_n_inputs, self._pt_type, fault_atoms)
            concretizer = Concretizer("[" + dummy_comp_name + "-" + self._pt_type.name + "].concr",
                                      self._comp_n_inputs, len(stage.pattern.input_ports),
                                      input_comp_ports=stage.nominal_module.input_ports,
                                      input_pattern_ports=stage.pattern.input_ports
                                      )
            abstractor = Abstractor("[" + dummy_comp_name + "-" + self._pt_type.name + "].abstr",
                                    len(stage.pattern.output_ports),
                                    output_pattern_ports=stage.pattern.output_ports,
                                    output_comp_port=stage.nominal_module.output_ports
                                    )
            behaviour_formula = And(stage.behaviour_formula, concretizer.behaviour_formula,
                                    abstractor.behaviour_formula)
            # Quantify out non-boolean variables
            dummy_qe_formula =  self.__apply_qe(behaviour_formula, fault_atoms + concretizer.input_ports + abstractor.output_ports)
            dummy_qe_formula_str = dummy_qe_formula.serialize()
            # Print formula on file
            with open(file_name, "w") as cache_file:
                cache_file.write(dummy_qe_formula_str)
        else:
            # Import formula from cache
            with open(file_name, "r") as cache_file:
                dummy_qe_formula_str = cache_file.read()
        # Parse string and extract SMT formula
        qe_formula = dummy_qe_formula_str.replace(dummy_comp_name, self._comp_name)
        for idx, f_atom in enumerate(self._fault_atoms):
            qe_formula = qe_formula.replace(self._comp_name + "_F" + str(idx), f_atom.serialize())

        formula = parse(qe_formula)

        # Check
        # with Solver("z3") as solver:
        #    print(solver.is_sat(Not(Implies(self._behaviour_formula, formula))))
        return formula

    def __apply_qe(self, formula, to_keep_atoms):
        # Define callback called each time mathsat finds a new model
        def callback(model, converter, result):
            # Convert back the mathsat model to a pySMT formula
            py_model = [converter.back(v) for v in model]
            # Append the module to the result list
            #print(py_model)
            result.append(And(py_model))
            return 1  # go on

        # Create a msat converter
        msat = Solver(name="msat")
        converter = msat.converter
        # add the csa formula to the solver
        msat.add_assertion(formula)
        result = []
        # Directly invoke mathsat APIs
        mathsat.msat_all_sat(msat.msat_env(),
                             [converter.convert(atom) for atom in to_keep_atoms],
                             # Convert the pySMT term into a MathSAT term
                             lambda model: callback(model, converter, result))
        return Or(result)


class Concretizer(Component):
    """
    Class representing a Concretizer component
    """

    def __init__(self, name: str, comp_n_inputs: int, pattern_n_inputs: int, input_ports: list = None,
                 input_pattern_ports: list = None, input_comp_ports: list = None):
        """
        Create a concretizer component
        :param name: name of the concretizer
        :param comp_n_inputs: number of inputs of the nominal component
        :param pattern_n_inputs: number of inputs of the pattern
        :param input_ports: (optional) input ports
        :param input_pattern_ports: (optional) output ports related to the pattern's inputs
        :param input_comp_ports: (optional) output ports related to the component's inputs
        """
        # Define input and output ports
        if input_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx)) for idx in range(pattern_n_inputs)]
        if input_comp_ports is None or input_pattern_ports is None:
            output_ports = [Symbol(name + ".o" + str(idx), REAL) for idx in range(comp_n_inputs + pattern_n_inputs)]
            input_pattern_ports = output_ports[:comp_n_inputs]
            input_comp_ports = output_ports[:comp_n_inputs]
        else:
            output_ports = input_comp_ports + input_pattern_ports
        self._output_pattern_ports = input_pattern_ports
        self._output_comp_ports = input_comp_ports
        # First component output ports and then pattern's output ports
        super(Concretizer, self).__init__(name, ComponentType.CONCRETIZER, input_ports, output_ports)

        # TODO: check this:
        #  the number of pattern's inputs should be a multiple of the number of the component's inputs
        assert len(input_pattern_ports) % len(
            input_comp_ports) == 0, "[Concretizer] Incompatible number of pattern's inputs and component's inputs"
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

    def __init__(self, name: str, pattern_n_outputs: int, output_ports: list = None, output_pattern_ports: list = None,
                 output_comp_port: Symbol = None):
        """
        Create an Abstractor
        :param name: name of the abstractor
        :param pattern_n_outputs: number of inputs corresponding to the pattern's output
        :param output_ports: (optional) list of output ports
        :param input_pattern_ports: (optional) list of input ports corresponding to the outputs of the patter
        :param output_comp_port: (optional)  input portscorresponding to the output of the nominal component
        """
        # Define input and output ports
        if output_ports is None:
            output_ports = [Symbol(name + ".o" + str(idx)) for idx in range(pattern_n_outputs)]
        if output_comp_port is None or output_pattern_ports is None:
            input_ports = [Symbol(name + ".i" + str(idx), REAL) for idx in range(1 + pattern_n_outputs)]
            output_pattern_ports = input_ports[1:]
            output_comp_port = input_ports[:1]
        else:
            input_ports = output_comp_port + output_pattern_ports
        self._output_pattern_ports = output_pattern_ports
        self._output_comp_port = output_comp_port[0]
        super(Abstractor, self).__init__(name, ComponentType.ABSTRACTOR, input_ports, output_ports)

        # The number of pattern's input port and abstractor's output ports have to be the same
        assert len(output_pattern_ports) == len(output_ports), "[Abstractor] number of pattern's outputs and abstractor's outputs have to be the same"
        # Define behaviour
        out_constraints = []
        for idx, patt_port in enumerate(self._output_pattern_ports):
            out_constraints.append(
                Iff(
                    Equals(
                        patt_port,
                        self._output_comp_port
                    ),
                    self._output_ports[idx]
                )
            )
        self._behaviour_formula = And(out_constraints)


# Test - Example
if __name__ == "__main__":
    csa = Csa("C1", 1, PatternType.TMR_V111, [Symbol("F0"), Symbol("F1"), Symbol("F2"), Symbol("F3")])
    print(csa.behaviour_formula.serialize())
    print(csa.get_qe_formula().serialize())