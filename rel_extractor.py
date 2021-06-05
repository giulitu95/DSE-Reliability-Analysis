from pysmt.shortcuts import *
import utils
import queue
import networkx as nx
from enum import Enum


class NodeType(Enum):
    LEAF = 1
    CONFIG = 2
    FAULT = 3


class Node:
    def __init__(self, type, idx, rel):
        self._type = type
        self._idx = idx
        self._rel = rel

    @property
    def rel(self):
        return self._rel

    @property
    def type(self):
        return self._type


class ConfigNode(Node):
    def __init__(self, var, idx):
        self._var = var
        self._rel = Symbol("rel" + "_" + self._var.serialize() + "-" + str(idx), REAL)
        self._ite_f = None
        super().__init__(NodeType.CONFIG, idx, self._rel)

    @property
    def var(self):
        return self._var


class FaultNode(Node):
    def __init__(self, var, idx):
        self._var = var
        self._rel = Symbol("rel" + "_" + self._var.serialize() + "-" + str(idx), REAL)
        super().__init__(NodeType.FAULT, idx, self._rel)

    @property
    def var(self):
        return self._var


class LeafNode(Node):
    def __init__(self, value, idx):
        self._value = value
        if self._value:
            self._rel = Symbol("rel" + "_TRUE-" + str(idx), REAL)
        else:
            self._rel = Symbol("rel" + "_FALSE-" + str(idx), REAL)
        super().__init__(NodeType.LEAF, idx, self._rel)

    @property
    def value(self):
        return self._value


class Extractor:

    def __init__(self, formula, cfg_symbols, f_symbols2prob, order=None):
        print("[Extractor] Create CCE-ROBDD...")
        min_bdd = Solver(name="bdd")
        # create bdd converter
        min_converter = min_bdd.converter
        # Import cudd manager
        self._bdd_mng = min_bdd.ddmanager
        if order is not None:
            for var in order:
                min_converter.declare_variable(var)
            self._formula = min_converter.convert(formula)
        else:
            self._formula = min_converter.convert(formula)
            print("[Extractor]    Apply SIFT algorithm,,,")
            self._bdd_mng.ReduceHeap(4, 0)
            print("[Extractor]    Done!")
        print("[Extractor] Done!")
        # map cudd index - pySMT variable
        self._idx2var = min_converter.idx2var
        utils.bdd_dump_dot(self._formula, self._bdd_mng, self._idx2var)
        self._f_symbols2prob = f_symbols2prob
        conf_symbol2type = {k: NodeType.CONFIG for k in cfg_symbols}
        fault_symbols2type = {k: NodeType.FAULT for k, _ in self._f_symbols2prob.items()}
        self._symbols2type = dict(conf_symbol2type)
        self._symbols2type.update(fault_symbols2type)
        self._rel_symbol = Symbol("Rel", REAL)

    def _get_rel_formula(self, c_r, probability, r_f, r_t):
        return Equals(
            c_r,
            Plus(
                Times(
                    probability,
                    r_t
                ),
                Times(
                    Minus(
                        Real(1),
                        probability
                    ),
                    r_f
                )
            )
        )

    def _get_tree(self, root):
        """
        given a bdd node, it traverses the cce bdd and prepares a networkx tree representing a bdd
        :param root: root of the cce bdd (cudd node)
        :return: networkx graph representing the bdd
        """
        node_idx = 0
        c = 0
        if self._bdd_mng.IsComplement(root):
            c = (c + 1) % 2
        nx_tree = nx.DiGraph()
        node2idx = {}
        stack = queue.LifoQueue()
        stack.put(((c, root), None, None))
        nx_tree.add_node(-1, data=LeafNode(True, -1))
        nx_tree.add_node(-2, data=LeafNode(False, -2))
        while not stack.empty():
            current, predecessor, branch = stack.get()
            c, node = current
            if current not in node2idx and not self._bdd_mng.IsConstant(node):
                e = self._bdd_mng.E(node)
                t = self._bdd_mng.T(node)
                e_c = c
                t_c = c
                if self._bdd_mng.IsComplement(e): e_c = (e_c + 1) % 2
                if self._bdd_mng.IsComplement(t): t_c = (t_c + 1) % 2
                stack.put(((t_c, t), current, 1))
                stack.put(((e_c, e), current, 0))
                if self._symbols2type[self._idx2var[node.NodeReadIndex()]] == NodeType.CONFIG:
                    nx_tree.add_node(node_idx, data=ConfigNode(self._idx2var[node.NodeReadIndex()], node_idx))
                else:
                    nx_tree.add_node(node_idx, data=FaultNode(self._idx2var[node.NodeReadIndex()], node_idx))
                if predecessor is not None:
                    if branch == 1:
                        nx_tree.add_edge(node2idx[predecessor], node_idx, branch=1)
                    else:
                        nx_tree.add_edge(node2idx[predecessor], node_idx, branch=0)
                node2idx[current] = node_idx
                node_idx = node_idx + 1
            else:
                if predecessor is not None:
                    if self._bdd_mng.IsConstant(node):
                        if c == 0:
                            curr_idx = -1
                        else:
                            curr_idx = -2
                    else:
                        curr_idx = node2idx[current]
                    if branch == 1:
                        nx_tree.add_edge(node2idx[predecessor], curr_idx, branch=1)
                    else:
                        nx_tree.add_edge(node2idx[predecessor], curr_idx, branch=0)
        return nx_tree

    def extract_reliability(self):
        """
        Perform a dfs over a networkx representing the bdd in order to create the reliability formula
        :return: reliability formula
        """
        print("[Extractor] Prepare nx OBDD...")
        tree = self._get_tree(self._formula)
        print("[Extractor] Done")
        rel_formulas = []
        # 1th dfs: Define rel variable for each fault node and ite variable for each conf node
        root = tree.nodes[0]
        root_data = root['data']
        rel = root_data.rel
        print("[Extractor] Apply algorithm (DFS)")
        if root_data.type != NodeType.LEAF:
            f_data = None
            t_data = None
            for neighbour, data in tree.adj[0].items():
                if data['branch'] == 0:
                    f_data = tree.nodes[neighbour]['data']
                else:
                    t_data = tree.nodes[neighbour]['data']

            assert f_data is not None and t_data is not None, "A node of the bdd has not 2 neighbours"
            if root_data.type == NodeType.FAULT:
                rel_formulas.append(
                    self._get_rel_formula(root_data.rel, self._f_symbols2prob[root_data.var], f_data.rel, t_data.rel))
            else:
                rel_formulas.append(
                    Ite(
                        root_data.var,
                        Equals(root_data.rel, t_data.rel),
                        Equals(root_data.rel, f_data.rel)
                    )
                )
        else:
            assert True, "Valid or unsatisfiable formulas are not accepted"

        for (s, d) in nx.dfs_edges(tree, source=0):
            node_data = tree.nodes[d]['data']
            branch = tree.edges[(s, d)]['branch']
            f_data = None
            t_data = None
            if node_data.type != NodeType.LEAF:
                for neighbour, data in tree.adj[d].items():
                    if data['branch'] == 0:
                        f_data = tree.nodes[neighbour]['data']
                    else:
                        t_data = tree.nodes[neighbour]['data']
                assert f_data is not None and t_data is not None, "A node of the bdd has not 2 neighbours"
                if node_data.type == NodeType.FAULT:  # case fault node
                    rel_formulas.append(
                        self._get_rel_formula(node_data.rel, self._f_symbols2prob[node_data.var], f_data.rel,
                                              t_data.rel))
                else:  # case config node
                    rel_formulas.append(
                        Ite(
                            node_data.var,
                            Equals(node_data.rel, t_data.rel),
                            Equals(node_data.rel, f_data.rel)
                        )
                    )
            else:  # case leaf
                if node_data.value:
                    rel_formulas.append(Equals(node_data.rel, Real(1)))
                else:
                    rel_formulas.append(Equals(node_data.rel, Real(0)))
        print("[Extractor] Done!")
        return And(And(rel_formulas), Equals(self._rel_symbol, rel))

    @property
    def fault_symbols2prob(self):
        return self._f_symbols2prob

    @property
    def rel_symbol(self):
        return self._rel_symbol
