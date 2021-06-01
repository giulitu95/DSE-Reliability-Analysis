from patterns import PatternType, TmrV111Definition, TmrV111
from components.csa import Csa
from pysmt.shortcuts import *
import math


class ArchNode:
    """
    Class provinding the methods for creating the formulas associated to a specific component of the architecture
    """
    def __init__(self, pt_library: list, comp_name: str, n_predecessors, next_archnodes: list = None):
        """
        Create an Architecture Node
        :param pt_library: list of pattern type
        :param comp_name: name of component
        :param next_archnodes: list of ArchNode instances indicating the component connected to the current one
        :param n_predecessors: number of predecessor components which are linked to the current node
        """
        # Check the pattern which requires the highest number of fault atoms:
        self._max_n_f = 0
        for pt in pt_library:
            if pt.pt_type == PatternType.TMR_V111:
                if self._max_n_f < TmrV111.n_f_atoms:
                    self._max_n_f = TmrV111.n_f_atoms
            else:
                NotImplementedError()
            # TODO: do this for all patterns:
            #  elif: pt.pt_type == PatternType.TMR_V123
            #  ...
        # create list of available fault atoms
        self._fault_atoms = [Symbol(comp_name + "_F" + str(idx)) for idx in range(self._max_n_f)]
        # prepare configuration atoms
        if len(pt_library) > 1:
            n_conf_atoms = math.ceil(math.log(len(pt_library), 2))
        else:
            n_conf_atoms = 1
        # List of configuration atoms for this csa
        self._conf_atoms = [Symbol("CONF_" + comp_name + "[" + str(idx) +"]") for idx in range(n_conf_atoms)]
        # check invalid configurations
        invalid_conf = []
        for idx in range(len(pt_library), (2 ** n_conf_atoms)):
            bin_str = '{0:0{l}b}'.format(idx, l = len(self._conf_atoms))
            conf = []
            for i, bin in enumerate(bin_str):
                if bin == '0': conf.append(Not(self._conf_atoms[i]))
                else: conf.append(self._conf_atoms[i])
            invalid_conf.append(And(conf))
        self._conf_formula = And( # Here we exclude invalid configurations
            Not(Or(invalid_conf))
        )
        self._csa_list = []
        self._f_atoms2prob = {}
        prob_constraints = []
        # create probability symbols (real)
        for f_idx, f_atom in enumerate(self._fault_atoms):
            self._f_atoms2prob[f_atom] = Symbol("p" + str(f_idx) + "_" + comp_name, REAL)

        # - prepare list of csa for each possible pattern-combination
        # - assign non functional parameters to the probability symbol
        for idx, pt in enumerate(pt_library):
            conf = self.get_conf_by_index(idx)
            if pt.pt_type == PatternType.TMR_V111:
                # create Csa
                pt_def = TmrV111Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )
            # TODO: do this for all patterns:
            #  elif: pt.pt_type == PatternType.TMR_V123
            #  ...

        self._prob_constraints = And(prob_constraints)

        # Constraints which describe the connections between components
        self._linker_constr = None
        # They say whether a pattern (configuration) con be linked to another pattern (configuration)
        self._compatibility_constr = None
        if next_archnodes is not None:
            # link the csa of the current node with the csa of the next node
            linker_constr = []
            compatibility_constr = []
            for c_idx, current_csa in enumerate(self._csa_list):
                # iterate over the current csa
                comp2comp_constr = []
                conf = self.get_conf_by_index(c_idx)
                for next_node in next_archnodes:
                    # iterate over the next archnodes
                    for n_idx, next_csa in enumerate(next_node.csa_list):
                        # iterate over the csa of the next archnode
                        if len(current_csa.output_ports) == 1:
                            # if the csa has only one output, then it can be connected with every next csa
                            for in_port in next_csa.input_ports:
                                comp2comp_constr.append(Iff(current_csa.output_ports[0], in_port))
                        elif len(current_csa.output_ports) == len(next_csa.input_ports):
                            # if 2 csa have compatible outputs-inputs then, they can be connected together
                            for idx in range(len(current_csa.output_ports)):
                                comp2comp_constr.append(Iff(current_csa.output_ports[idx], next_csa.input_ports[idx]))
                        else:
                            # patterns are not sequentially compatible so, add the formula
                            # current_configuration -> ~next_configuration
                            compatibility_constr.append(Implies(conf, Not(next_node.get_conf_by_index(n_idx))))
                linker_constr.append(
                    Implies(
                        conf,
                        And(comp2comp_constr)
                    )
                )
            self._linker_constr = And(linker_constr)
            self._compatibility_constr = And(compatibility_constr)
        else:
            # It is the last node! (tle)
            pass

    def get_qe_formulas(self) -> list:
        """
        Retrieve a list of boolean formula obtained applying AllSMT to every
        :return: the list of boolean formula for each csa
        """
        formulas = []
        for csa in self._csa_list:
            formulas.append(csa.get_qe_formula())
        return formulas

    def get_conf_by_index(self, index: int):
        """
        Given an index retrieve a formula representing that configuration
        :param index: index
        :return: Boolean formula in DNF which describe the configuration
        """
        bin_str = '{0:0{l}b}'.format(index, l = len(self._conf_atoms))
        conf = []
        for i, bin in enumerate(bin_str):
            if bin == '0': conf.append(Not(self._conf_atoms[i]))
            else: conf.append(self._conf_atoms[i])
        return And(conf)

    @property
    def csa_list(self) -> list:
        """
        :return: list of csa of the node
        """
        return self._csa_list

    @property
    def linker_constr(self):
        """
        :return: Formula representing the connections between the various csa
        """
        return self._linker_constr

    @property
    def compatibility_constr(self):
        """
        :return: Formula representing the available connections between CSA
        """
        return self._compatibility_constr

    @property
    def conf_formula(self):
        """
        :return: Formula representing the available configurations
        """
        return self._conf_formula

    @property
    def prob_constraints(self):
        """
        :return: A formula which assigns to each probability symbol a value (depending on configuration)
        """
        return self._prob_constraints

    @property
    def f_atoms2prob(self):
        """
        :return: A map which for every fault atom it's assiciated a probability real symbol
        """
        return self._f_atoms2prob

    @property
    def conf_atoms(self):
        """
        :return: The list of configuration atoms
        """
        return self._conf_atoms

    @property
    def fault_atoms(self):
        """
        :return: The list of fault atoms
        """
        return self._fault_atoms

# Test - Example
from patterns import TmrV111Spec
from params import NonFuncParamas
if __name__ == "__main__":
    an2 = ArchNode([TmrV111Spec("TMR_V111_A", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))], "C2", 2)
    an1 = ArchNode([TmrV111Spec("TMR_V111_A", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1)),
                    TmrV111Spec("TMR_V111_B", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1)),
                    TmrV111Spec("TMR_V111_C", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))],
                   "C1", 1, next_archnodes=[an2])

    qe1 = an1.get_qe_formulas()
    qe2 = an2.get_qe_formulas()


