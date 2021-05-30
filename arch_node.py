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
        # prepare list of csa for each possible pattern-combination
        self._csa_list = []
        for pt in pt_library:
            if pt.pt_type == PatternType.TMR_V111:
                pt_def = TmrV111Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                self._csa_list.append(Csa(pt_def))
        # prepare configuration atoms
        if len(pt_library) > 1:
            n_conf_atoms = math.ceil(math.log(len(pt_library), 2))
        else:
            n_conf_atoms = 1
        self._conf_atoms = [Symbol("CONF_" + comp_name + "[" + str(idx) +"]") for idx in range(n_conf_atoms)]
        # check invalid configurations
        invalid_conf = []
        valid_conf = []
        for idx in range((2 ** n_conf_atoms)):
            bin_str = '{0:0{l}b}'.format(idx, l = len(self._conf_atoms))
            conf = []
            for i, bin in enumerate(bin_str):
                if bin == '0': conf.append(Not(self._conf_atoms[i]))
                else: conf.append(self._conf_atoms[i])
            if idx >= len(pt_library):
                invalid_conf.append(And(conf))
            else:
                valid_conf.append(And(conf))
        self._conf_formula = And(
            Or(valid_conf),
            Not(Or(invalid_conf))
        )
        self._linker_constr = None
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

    def get_conf_by_index(self, index: int):
        bin_str = '{0:0{l}b}'.format(index, l = len(self._conf_atoms))
        conf = []
        for i, bin in enumerate(bin_str):
            if bin == '0': conf.append(Not(self._conf_atoms[i]))
            else: conf.append(self._conf_atoms[i])
        return And(conf)

    @property
    def csa_list(self):
        return self._csa_list



'''# Test - Example
from patterns import TmrV111Spec
from params import NonFuncParamas
if __name__ == "__main__":
    an2 = ArchNode([TmrV111Spec("TMR_V111_A", [], NonFuncParamas(2,3))], "C2", 2)
    an1 = ArchNode([TmrV111Spec("TMR_V111_A", [], NonFuncParamas(2,3)), TmrV111Spec("TMR_V111_B", [], NonFuncParamas(2,3)), TmrV111Spec("TMR_V111_C", [], NonFuncParamas(2,3))], "C1", 1, next_archnodes=[an2])

'''