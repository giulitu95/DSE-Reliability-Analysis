import networkx as nx
from arch_node import ArchNode
from pysmt.shortcuts import *


class RelTools:
    """
    Class where all the needed formulas are created.
    """
    def __init__(self, arch_graph):
        """
        The constructor accepts the architecture's graph representing the topology of the architecture
        :param
        arch_graph: networkx graph describing the connections between components. The index of the node corresponds
        to its name. Each node has to have an attribute pt_library where a library of pattern is specified
        """
        self._arch_graph = arch_graph
        self._nxnode2archnode = {}
        # create all archnodes
        for node in nx.dfs_postorder_nodes(arch_graph):
            if node not in self._nxnode2archnode:
                an_successors = [self._nxnode2archnode[succ] for succ in arch_graph.successors(node)]
                # TODO: fix this!!!
                if len(list(arch_graph.predecessors(node))) == 0: n_pred = 1
                else: n_pred = len(list(arch_graph.predecessors(node)))
                an = ArchNode(arch_graph.nodes[node]['pt_library'], node,  n_pred, an_successors)
                self._nxnode2archnode[node] = an
        # Import all formulas from each ardch node
        linker_constr = []
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

    def get_qe_formula(self):
        """
        :return: A boolena formula representing the architecture
        """
        qe_formulas = []
        for _, an in self._nxnode2archnode.items():
            qe_formulas.append(And(an.get_qe_formulas()))
        return And(qe_formulas)

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


# Test - Example
from patterns import TmrV111Spec
from params import NonFuncParamas
if __name__ == "__main__":
    pt_lib2 = [TmrV111Spec("TMR_V111_A", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))]
    pt_lib1 = [TmrV111Spec("TMR_V111_A", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1)),
                    TmrV111Spec("TMR_V111_B", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1)),
                    TmrV111Spec("TMR_V111_C", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))]

    g = nx.DiGraph()
    g.add_nodes_from([("C1", {'pt_library': pt_lib1}),
                      ("C2", {'pt_library': pt_lib2})])
    g.add_edge('C1', 'C2')
    r = RelTools(g)
    qe = r.get_qe_formula()
    print("Qe formula:")
    print(qe)
    print("Linker constraints")
    print(r.linker_constr)
    print("Compatibility constraints")
    print(r.compatibility_constr)
    print("Configurations formula")
    print(r.conf_formula)
    print("Probability constraints")
    print(r.prob_constr)
