#!/usr/bin/env python

from patterns import PatternType, PlainDefinition, CmpDefinition, TmrV111Definition, TmrV123Definition, TmrV010Definition, TmrV101Definition, TmrV001Definition, TmrV011Definition, TmrV110Definition, TmrV100Definition, TmrV122Definition, TmrV112Definition, TmrV120Definition, TmrV102Definition, TmrV012Definition, Xooy_3oo4_Definition
from components.csa import Csa
from pysmt.shortcuts import *
from collections import defaultdict
import math

__author__ = "Giuliano Turri, Antonio Tierno"

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
            if self._max_n_f < pt.pt_class.n_f_atoms:
                self._max_n_f = pt.pt_class.n_f_atoms
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
        self._csa2configs = defaultdict(list)
        self._f_atoms2prob = {}
        prob_constraints = []
        # create probability symbols (real)
        for f_idx, f_atom in enumerate(self._fault_atoms):
            self._f_atoms2prob[f_atom] = Symbol("p" + str(f_idx) + "_" + comp_name, REAL)

        # - prepare list of csa for each possible pattern-combination
        # - assign non functional parameters to the probability symbols
        pt_type2csa = {}
        self._conf2pt = {}
        for idx, pt in enumerate(pt_library):
            conf = self.get_conf_by_index(idx)
            self._conf2pt[conf] = pt
            if pt.pt_type == PatternType.TMR_V111:
                if pt.pt_type not in pt_type2csa:
                    # create Csa only if a csa of the same pattern has not been created
                    pt_def = TmrV111Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
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
                if len(self._fault_atoms) > 3:
                    for f_idx, f_atom in enumerate(self._fault_atoms[4:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V123:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV123Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3:6])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:6]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 6:
                    for f_idx, f_atom in enumerate(self._fault_atoms[7:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.PLAIN:
                if pt.pt_type not in pt_type2csa:
                    pt_def = PlainDefinition(comp_name, n_predecessors, self._fault_atoms[0])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                prob_constraints.append(Implies(
                    conf,
                    Equals(self._f_atoms2prob[self._fault_atoms[0]], Real(pt.module_params[0]))
                ))
                if len(self._fault_atoms) > 1:
                    for f_idx, f_atom in enumerate(self._fault_atoms[2:]):  # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf, Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.CMP:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = CmpDefinition(comp_name, n_predecessors, self._fault_atoms[:2], self._fault_atoms[2])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:2]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # comparator:
                for f_idx, f_atom in enumerate(self._fault_atoms[2]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.comparator_param[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 2:
                    for f_idx, f_atom in enumerate(self._fault_atoms[3:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V001:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV001Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 3:
                    for f_idx, f_atom in enumerate(self._fault_atoms[4:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V101:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV101Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 3:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V010:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV010Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 3:
                    for f_idx, f_atom in enumerate(self._fault_atoms[4:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V011:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV011Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 3:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V110:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV110Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 5:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V100:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV100Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 3:
                    for f_idx, f_atom in enumerate(self._fault_atoms[4:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V122:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV122Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3:5])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:5]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 5:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V112:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV112Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3:5])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:5]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 5:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V120:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV120Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3:5])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:5]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 5:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V102:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV102Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3:5])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:5]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 5:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.TMR_V012:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = TmrV012Definition(comp_name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3:5])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:5]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                if len(self._fault_atoms) > 5:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))

            elif pt.pt_type == PatternType.Xooy_3oo4:
                # Create csa
                if pt.pt_type not in pt_type2csa:
                    pt_def = Xooy_3oo4_Definition(comp_name, n_predecessors, self._fault_atoms[:4], self._fault_atoms[4])
                    csa = Csa(pt_def)
                    pt_type2csa[pt.pt_type] = csa
                else:
                    csa = pt_type2csa[pt.pt_type]
                self._csa2configs[csa].append(conf)
                # assign non-functional parameters
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:4]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[4]], Real(pt.voters_params.fault_prob))
                    )
                )
                if len(self._fault_atoms) > 4:
                    for f_idx, f_atom in enumerate(self._fault_atoms[6:]): # fix the other variables to an arbitrary number (otherwise an infinite number of models exist)
                        prob_constraints.append(Implies(conf,Equals(self._f_atoms2prob[f_atom], Real(0))))
            else:
                NotImplementedError()


            # TODO: do this for all patterns:
            #  elif: pt.pt_type == PatternType.TMR_V123
            #  ...

        self._prob_constraints = And(prob_constraints)

        # Constraints which describe the connections between components (no constraints is equivalent to the True constraint)
        self._linker_constr = TRUE()
        # They say whether a pattern (configuration) con be linked to another pattern (configuration)
        self._compatibility_constr = TRUE()
        linker_constr = []
        if next_archnodes :
            # link the csa of the current node with the csa of the next node
            compatibility_constr = []
            for next_node in next_archnodes:
                # iterate over the next archnodes
                for next_csa, next_configs in next_node.csa2configs.items():
                    # iterate over the csa of the next archnode
                    to_connect_ports = next_csa.get_update_available_ports()
                    for csa, configs in self._csa2configs.items():
                        # iterate over the current csa
                        comp2comp_constr = []
                        if len(csa.output_ports) == 1:
                            # if the csa has only one output, then it can be connected with every next csa
                            for in_port in to_connect_ports:
                                comp2comp_constr.append(Iff(csa.output_ports[0], in_port))
                        elif len(csa.output_ports) == len(to_connect_ports):
                            # if 2 csa have compatible outputs-inputs then, they can be connected together
                            for idx in range(len(to_connect_ports)):
                                comp2comp_constr.append(Iff(csa.output_ports[idx], to_connect_ports[idx]))
                        else:
                            # patterns are not sequentially compatible so, add the formula
                            # current_configuration -> ~next_configuration
                            compatibility_constr.append(
                                Implies(
                                    Or(configs),
                                    Not(Or(next_configs))))
                        linker_constr.append(
                            Implies(
                                Or(configs),
                                And(comp2comp_constr)
                            )
                        )
            self._compatibility_constr = And(compatibility_constr)
        else:
            # It is the last node! (tle)
            for csa, configs in self._csa2configs.items():
                linker_constr.append(Implies(
                    Or(configs),
                    Not(And(csa.output_ports))
                ))

        self._linker_constr = And(linker_constr)

    def get_qe_formulas(self) -> list:
        """
        Retrieve a list of boolean formula obtained applying AllSMT to every
        :return: the list of boolean formula for each csa
        """
        formulas = []
        for csa, _ in self._csa2configs.items():
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
    def csa2configs(self) -> dict:
        """
        :return: list of csa of the node
        """
        return self._csa2configs

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

    @property
    def conf2pt(self):
        """
        :return: A dictionary which assign a pattern spec to every configuration
        """
        return self._conf2pt
    @property
    def input_ports(self):
        """
        :return: The list of input ports of this
        """
        input_ports = []
        for csa, _ in self._csa2configs.items():
            input_ports.extend(csa.input_ports)
        return  input_ports

    @property
    def output_ports(self):
        output_ports = []
        for csa, _ in self._csa2configs.items():
            output_ports.extend(csa.output_ports)
        return output_ports



'''# Test - Example
from patterns import TmrV111Spec
from params import NonFuncParamas
if __name__ == "__main__":
    an4 = ArchNode([TmrV111Spec("TMR_V111_A",
                                [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                                NonFuncParamas(0.1))], "C4", 3)
    an1 = ArchNode([TmrV111Spec("TMR_V111_A", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))], "C1", 1, next_archnodes=[an4])
    an2 = ArchNode([TmrV111Spec("TMR_V111_A",[NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],NonFuncParamas(0.1))], "C2", 1, next_archnodes=[an4])
    an3 = ArchNode([TmrV111Spec("TMR_V111_A",
                                [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                                NonFuncParamas(0.1))], "C3", 1, next_archnodes=[an4])



    qe1 = an1.get_qe_formulas()
    qe2 = an2.get_qe_formulas()'''
