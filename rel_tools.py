#!/usr/bin/env python

import networkx as nx
from arch_node import ArchNode
from pysmt.shortcuts import *
from rel_extractor import Extractor
from allsmt import allsmt
import repycudd

__author__ = "Giuliano Turri"


class RelTools:
    """
    Class where all the needed formulas are created.
    """
    def __init__(self, arch_graph):
        """
        The constructor accepts the architecture's graph representing the topology of the architecture
        :param
        arch_graph: networkx graph describing the connections between components. The index of the node corresponds
        to its name. Each node has a type: 'COMP' or 'SOURCE'. COMP type indicates that the node represents a component
        while SOURCE indicates that the node represents a source of "data", this type of node is used to connect the
        first nodes of the architecture.
        Each COMP node has to have an attribute pt_library where a library of pattern is specified.
        """
        self._arch_graph = arch_graph
        self._nxnode2archnode = {}
        self._conf_atoms = []
        # create all archnodes
        linker_constr = []
        print("[Architecture] Initialize all csa")
        for node in nx.dfs_postorder_nodes(arch_graph):
            if node not in self._nxnode2archnode and arch_graph.nodes[node]['type'] == 'COMP':
                an_successors = [self._nxnode2archnode[succ] for succ in arch_graph.successors(node)]
                n_pred = len(list(arch_graph.predecessors(node)))
                an = ArchNode(arch_graph.nodes[node]['pt_library'], node,  n_pred, an_successors)
                self._nxnode2archnode[node] = an
                self._conf_atoms.extend(an.conf_atoms)
            elif arch_graph.nodes[node]['type'] == "SOURCE":
                # Input of the architecture must be nominal
                for succ in arch_graph.successors(node):
                    for csa, _ in self._nxnode2archnode[succ].csa2configs.items():
                        linker_constr.append(And(csa.input_ports))
        # Import all formulas from each ardch node
        compatibility_constr = []
        conf_formulas = []
        prob_constr = []
        self._f_atoms2prob = {}
        for _, an in self._nxnode2archnode.items():
            linker_constr.append(an.linker_constr)
            compatibility_constr.append((an.compatibility_constr))
            conf_formulas.append(an.conf_formula)
            prob_constr.append(an.prob_constraints)
            self._f_atoms2prob.update(an.f_atoms2prob)
        self._linker_constr = And(linker_constr)
        self._compatibility_constr = And(compatibility_constr)
        self._conf_formula = And(conf_formulas)
        self._prob_constr = And(prob_constr)

    def __get_qe_formula(self):
        """
        :return: A boolena formula representing the architecture
        """
        qe_formulas = []
        for _, an in self._nxnode2archnode.items():
            qe_formulas.append(And(an.get_qe_formulas()))
        return And(qe_formulas)

    def apply_arch_allsmt(self):
        to_keep_atoms = []
        for _, an in self._nxnode2archnode.items():
            to_keep_atoms.extend(an.fault_atoms)
            to_keep_atoms.extend(an.conf_atoms)
        print("[Architecture] Quantify out non-boolean variables of all CSA")
        formula = self.__get_qe_formula()
        print("[Architecture] Quantify out input and output ports")
        cutsets_formula = allsmt(And([formula, self._linker_constr, self._conf_formula]), to_keep_atoms)

        return cutsets_formula

    def extract_reliability_formula(self):
        # Create cut-sets formula
        formula = self.apply_arch_allsmt()
        bdd = Solver(name="bdd")
        converter = bdd.converter
        m1 = bdd.ddmanager
        bdd_formula = converter.convert(formula)  # converted formula
        id_var = converter.idx2var

        # Iterate over prime implicants, creating a pySMT formula representing primes
        # TODO: we could generate a bdd formula directly instead of a pysmt formula
        repycudd.set_iter_meth(2)
        conjunctions = []
        print("[Architecture] Create minimal-cutset formula (fiind PI)...")
        for prime in repycudd.ForeachPrimeIterator(m1, repycudd.NodePair(bdd_formula, bdd_formula)):
            prime_vec = [*prime]
            current_conj = []
            for i in range(len(prime_vec)):
                if prime_vec[i] == 1:
                    current_conj.append(id_var[i])
                elif prime_vec[i] != 2:
                    current_conj.append(Not(id_var[i]))
            #print(current_conj)
            conjunctions.append(And(current_conj))

        prime_formula = And(
            Or(conjunctions)
        )
        print("[Architecture] Done!")
        #print("- Minimal cutstets formula: ")
        #print(prime_formula)
        extractor = Extractor(prime_formula, self._conf_atoms, r.f_atoms2prob)
        rel_f = extractor.extract_reliability()
        return rel_f

    @property
    def f_atoms2prob(self):
        """
        :return: a dictionary mapping the fault atom of a component to its fault's probability
        """
        return self._f_atoms2prob

    @property
    def linker_constr(self):
        """
        :return: formula which describes the connections between the various patterns
        """
        return self._linker_constr

    @property
    def compatibility_constr(self):
        """
        :return: formula which excludes the connections between incompatible patterns
        """
        return self._compatibility_constr

    @property
    def conf_formula(self):
        """
        :return: formula which excludes unavailable configurations
        """
        return self._conf_formula

    @property
    def prob_constr(self):
        """
        :return: formula which binds a real value to each probability symbol
        """
        return self._prob_constr

    @property
    def conf_atoms(self):
        return self._conf_atoms

# Test - Example
from patterns import TmrV111Spec
from params import NonFuncParamas
if __name__ == "__main__":
    pt_lib1 = [     TmrV111Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1)),
                    TmrV111Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1)),
                    TmrV111Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))]
    pt_lib2 = [     TmrV111Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))]

    g = nx.DiGraph()
    g.add_nodes_from([  ("S1", {'type': 'SOURCE'}),
                        ("S2", {'type': 'SOURCE'}),
                        ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C2", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C3", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C4", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C5", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C6", {'type': 'COMP', 'pt_library': pt_lib1})])
    g.add_edge('S1', 'C1')
    g.add_edge('S2', 'C2')
    g.add_edge('C1', 'C3')
    g.add_edge('C1', 'C4')
    g.add_edge('C2', 'C4')
    g.add_edge('C2', 'C5')
    g.add_edge('C3', 'C6')
    g.add_edge('C4', 'C6')
    g.add_edge('C5', 'C6')

    r = RelTools(g)
    f = r.extract_reliability_formula()
    print("Reliability formula")
    print(f.serialize())

    print("Probability values")
    print(r.prob_constr.serialize())


