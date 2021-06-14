#!/usr/bin/env python

import networkx as nx
from arch_node import ArchNode
from pysmt.shortcuts import *
from rel_extractor import Extractor
import repycudd
import time

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
        self._var_order = []
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
                order = an.conf_atoms + an.input_ports + an.fault_atoms + an.output_ports
                self._var_order = order + self._var_order
            elif arch_graph.nodes[node]['type'] == "SOURCE":
                # Input of the architecture must be nominal
                for succ in arch_graph.successors(node):
                    for csa, _ in self._nxnode2archnode[succ].csa2configs.items():
                        linker_constr.append(And(csa.input_ports))
        # Import all formulas from each ardch node
        compatibility_constr = []
        conf_formulas = []
        prob_constr = []
        self._io_ports = []
        self._f_atoms2prob = {}
        self._conf2pt = {}
        for _, an in self._nxnode2archnode.items():
            linker_constr.append(an.linker_constr)
            compatibility_constr.append((an.compatibility_constr))
            conf_formulas.append(an.conf_formula)
            prob_constr.append(an.prob_constraints)
            self._f_atoms2prob.update(an.f_atoms2prob)
            self._io_ports.extend(an.input_ports)
            self._io_ports.extend(an.output_ports)
            self._conf2pt.update(an.conf2pt)
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

    def extract_reliability_formula(self, benchmark=None):
        time_start = time.perf_counter()
        # Get boolean formula of the architecture (in/out ports, fault atoms, cnf atoms)
        arch_formula = self.__get_qe_formula()
        if benchmark is not None: benchmark.arch_creation_time = time.perf_counter() - time_start
        total_time_start = time.perf_counter()
        # Get boolean formula of the architecture (in/out ports, fault atoms, cnf atoms)
        cut_sets = And([arch_formula, self._linker_constr])
        # Import cudd to create the OBDD
        cudd = Solver(name="bdd")

        # Quantify out input and output ports creating the obdd
        converter = cudd.converter
        # Fix a variable ordering
        for var in self._var_order:
            converter.declare_variable(var)
        mng = cudd.ddmanager
        print("[Architecture] Quantify out in-out ports and create BDD")
        time_start = time.perf_counter()
        bdd_formula = converter.convert(Exists(self._io_ports, cut_sets))  # Exists(io_ports, cutsets_formula)
        if benchmark is not None: benchmark.bdd_qelim_time = time.perf_counter() - time_start
        print("[Architecture] Done!")
        id_var = converter.idx2var

        # Create Minimal cutset formula
        # Iterate over prime implicants, creating a pySMT formula representing primes
        repycudd.set_iter_meth(2)
        conjunctions = []
        print("[Architecture] Create minimal-cutset formula (find PI)...")
        time_start = time.perf_counter()
        for prime in repycudd.ForeachPrimeIterator(mng, repycudd.NodePair(bdd_formula, bdd_formula)): # Iterate over PI
            prime_vec = [*prime]
            current_conj = []
            for i in range(len(prime_vec)):
                if prime_vec[i] == 1:
                    current_conj.append(mng.IthVar(i))
                elif prime_vec[i] != 2:
                    current_conj.append(mng.Not(mng.IthVar(i)))
            lit_ddarr = repycudd.DdArray(mng, len(current_conj)) # literal array: contains the literals of the prime implicants
            for lit in current_conj: lit_ddarr.Push(lit) # The PI is the conjunction of PI
            conjunctions.append(lit_ddarr.And())
        # Create array of PI
        pi_ddarr = repycudd.DdArray(mng, len(conjunctions))
        for pi in conjunctions: pi_ddarr.Push(pi)
        # Assemble minimal cutset formula
        p_formula = mng.And(
            pi_ddarr.Or(),
            converter.convert(self._conf_formula)
        )
        p_formula = mng.And(
            p_formula,
            converter.convert(self._compatibility_constr)
        )
        if benchmark is not None: benchmark.mincutsets_time = time.perf_counter() - time_start
        print("[Architecture] Done!")
        extractor = Extractor(p_formula, mng, converter.idx2var, self._conf_atoms, self._f_atoms2prob, benchmark=benchmark)
        time_start = time.perf_counter()
        rel_f = extractor.extract_reliability()
        if benchmark is not None:
            benchmark.rel_extraction_time = time.perf_counter() - time_start
            benchmark.total_ext_time = time.perf_counter() - total_time_start
        return extractor.rel_symbol, rel_f

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

    @property
    def conf2pt(self):
        return self._conf2pt

    @property
    def nxnode2archnode(self):
        return self._nxnode2archnode


'''# Test - Example
from patterns import TmrV111Spec, TmrV123Spec
from params import NonFuncParamas
if __name__ == "__main__":
    pt_lib1 = [
        TmrV111Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                    NonFuncParamas(0.1)),
        TmrV111Spec([NonFuncParamas(0.2), NonFuncParamas(0.3), NonFuncParamas(0.03), NonFuncParamas(0.2)],
                    NonFuncParamas(0.2))
    ]
    pt_lib2 = [
        TmrV123Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                    [NonFuncParamas(0.2), NonFuncParamas(0.3), NonFuncParamas(0.03), NonFuncParamas(0.2)])
    ]
    pt_lib3 = [
        TmrV123Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                    [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)])
    ]
    pt_lib4 = [
        TmrV123Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                    [NonFuncParamas(0.), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)]),
        TmrV111Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                    NonFuncParamas(0.1))
    ]
    # (A & B) | C: 110 - 111 - 001 - 011 - 101 10,01,11
    g = nx.DiGraph()
    g.add_nodes_from([  ("S1", {'type': 'SOURCE'}),
                        ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C2", {'type': 'COMP', 'pt_library': pt_lib1}),
    ])
    g.add_edge('S1', 'C1')
    g.add_edge('C1', 'C2')
    r = RelTools(g)
    rel, f = r.extract_reliability_formula()
    from pysmt.optimization.goal import MaximizationGoal, MinimizationGoal
    from pysmt.logics import QF_NRA

    max = MinimizationGoal(rel)
    print(f.serialize())
    with Optimizer(name="z3") as opt:
        opt.add_assertion(f)
        opt.add_assertion(r.prob_constr)
        opt.add_assertion(r.conf_formula)
        b = opt.optimize(max)
        if b is not None:
            a,c = b
            print(a)'''

    # (((CONF_C1[0] ? (rel_CONF_C1[0]-0 = rel_FALSE--2) : (rel_CONF_C1[0]-0 = rel_C1_F0-1))
    # & (rel_C1_F0-1 = ((p0_C1 * rel_C1_F1-12) + ((1.0 - p0_C1) * rel_C1_F1-2))) &
    # (rel_C1_F1-2 = ((p1_C1 * rel_C1_F2-11) + ((1.0 - p1_C1) * rel_C1_F3-3))) &
    # (rel_C1_F3-3 = ((p3_C1 * rel_CONF_C2[0]-10') + ((1.0 - p3_C1) * rel_CONF_C2[0]-4'))) &
    # (CONF_C2[0] ? ('rel_CONF_C2[0]-4 = rel_FALSE--2) : (rel_CONF_C2[0]-4 = rel_C2_F0-5)) &
    # (rel_C2_F0-5 = ((p0_C2 * rel_C2_F1-9) + ((1.0 - p0_C2) * rel_C2_F1-6))) &
    # (rel_C2_F1-6 = ((p1_C2 * rel_C2_F2-8) + ((1.0 - p1_C2) * rel_C2_F3-7))) &
    # (rel_C2_F3-7 = ((p3_C2 * rel_TRUE--1) + ((1.0 - p3_C2) * rel_FALSE--2))) &
    # (rel_FALSE--2 = 0.0) &
    # (rel_TRUE--1 = 1.0) &
    # (rel_C2_F2-8 = ((p2_C2 * rel_TRUE--1) + ((1.0 - p2_C2) * rel_C2_F3-7))) &
    # (rel_C2_F1-9 = ((p1_C2 * rel_TRUE--1) + ((1.0 - p1_C2) * rel_C2_F2-8))) &
    # (CONF_C2[0] ? (rel_CONF_C2[0]-10 = rel_FALSE--2) : (rel_\'CONF_C2[0]-10 = rel_TRUE--1)) &
    # (rel_C1_F2-11 = ((p2_C1 * rel_CONF_C2[0]-10) + ((1.0 - p2_C1) * rel_C1_F3-3))) &
    # (rel_C1_F1-12 = ((p1_C1 * rel_CONF_C2[0]-10) + ((1.0 - p1_C1) * rel_C1_F2-11)))) &
    # (Rel = 'rel_CONF_C1[0]-0))