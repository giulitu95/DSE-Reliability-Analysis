import networkx as nx
from arch_node import ArchNode
from pysmt.shortcuts import *
import mathsat


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
        # create all archnodes
        linker_constr = []
        print("[Architecture] Initialize all csa")
        for node in nx.dfs_postorder_nodes(arch_graph):
            if node not in self._nxnode2archnode and arch_graph.nodes[node]['type'] == 'COMP':
                an_successors = [self._nxnode2archnode[succ] for succ in arch_graph.successors(node)]
                n_pred = len(list(arch_graph.predecessors(node)))
                an = ArchNode(arch_graph.nodes[node]['pt_library'], node,  n_pred, an_successors)
                self._nxnode2archnode[node] = an
            elif arch_graph.nodes[node]['type'] == "SOURCE":
                # Input of the architecture must be nominal
                for succ in arch_graph.successors(node):
                    for csa in self._nxnode2archnode[succ].csa_list:
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

    def apply_allsmt(self):
        to_keep_atoms = []
        for _, an in self._nxnode2archnode.items():
            to_keep_atoms.extend(an.fault_atoms)
            to_keep_atoms.extend(an.conf_atoms)
        print("[Architecture] Compute qe of all CSA")
        formula = self.__get_qe_formula()
        # Define callback called each time mathsat finds a new model
        def callback(model, converter, result, i):
            # Convert back the mathsat model to a pySMT formula
            py_model = [converter.back(v) for v in model]
            # Append the module to the result list
            # print(py_model)
            result.append(And(py_model))
            i[0] = i[0]+1
            #print(i[0], end="\r")
            return 1  # go on
            # Create a msat converter
        msat = Solver(name="msat")
        converter = msat.converter
        # add the csa formula to the solver
        msat.add_assertion(And([formula, self._linker_constr, self._conf_formula]))
        result = []
        i = [0] #tmp
        # Directly invoke mathsat APIs
        print("[Architecture] Compute allSMT On the entire formula...")
        mathsat.msat_all_sat(msat.msat_env(),
                             [converter.convert(atom) for atom in to_keep_atoms],
                             # Convert the pySMT term into a MathSAT term
                             lambda model: callback(model, converter, result, i))
        res_formula =  Or(result)
        print("[Architecture] Done! " + str(i[0]) + " models found")
        return res_formula

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
    pt_lib1 = [     TmrV111Spec("TMR_V111_A", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))]
    pt_lib2 = [     TmrV111Spec("TMR_V111_B", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1)),
                    TmrV111Spec("TMR_V111_C", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))]

    g = nx.DiGraph()
    g.add_nodes_from([  ("S1", {'type': 'SOURCE'}),
                        ("S2", {'type': 'SOURCE'}),
                        ("S3", {'type': 'SOURCE'}),
                        ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C2", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C3", {'type': 'COMP', 'pt_library': pt_lib1}),
                        ("C4", {'type': 'COMP', 'pt_library': pt_lib2})])
    g.add_edge('S1', 'C1')
    g.add_edge('S2', 'C2')
    g.add_edge('S3', 'C3')
    g.add_edge('C1', 'C4')
    g.add_edge('C2', 'C4')
    g.add_edge('C3', 'C4')

    r = RelTools(g)
    f = r.apply_allsmt()

    print("Linker constraints")
    print(r.linker_constr.serialize())
    print("Compatibility constraints")
    print(r.compatibility_constr)
    print("Configurations formula")
    print(r.conf_formula)
    print("Probability constraints")
    print(r.prob_constr)
    #print("~~~~~~~")
    #print(f.serialize())

# (('[C1-TMR_V111_A].concr.i0' & '[C1-TMR_V111_A].concr.i1' & '[C1-TMR_V111_A].concr.i2') &
# ('[C2-TMR_V111_A].concr.i0' & '[C2-TMR_V111_A].concr.i1' & '[C2-TMR_V111_A].concr.i2') &
# ('[C3-TMR_V111_A].concr.i0' & '[C3-TMR_V111_A].concr.i1' & '[C3-TMR_V111_A].concr.i2') &
# ((! 'CONF_C4[0]') -> (! '[C4-TMR_V111_A].abstr.o0')) &

# ((! 'CONF_C1[0]') -> (    ('[C1-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i0') &
#                           ('[C1-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i3') &
#                           ('[C1-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i6'))) &
# ((! 'CONF_C2[0]') ->      (('[C2-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i0') &
#                           ('[C2-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i3') &
#                           ('[C2-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i6'))) &
# ((! 'CONF_C3[0]') ->      (('[C3-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i0') &
#                           ('[C3-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i3') &
#                           ('[C3-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i6'))))


# (('[C1-TMR_V111_A].concr.i0' & '[C1-TMR_V111_A].concr.i1' & '[C1-TMR_V111_A].concr.i2') &
# ('[C2-TMR_V111_A].concr.i0' & '[C2-TMR_V111_A].concr.i1' & '[C2-TMR_V111_A].concr.i2') &
# ('[C3-TMR_V111_A].concr.i0' & '[C3-TMR_V111_A].concr.i1' & '[C3-TMR_V111_A].concr.i2') &

# ((! 'CONF_C4[0]') -> (! '[C4-TMR_V111_A].abstr.o0')) &
# ((! 'CONF_C1[0]') -> (    ('[C1-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i0') &
#                           ('[C1-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i3') &
#                           ('[C1-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i6'))) &
# ((! 'CONF_C2[0]') -> (    ('[C2-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i1') &
#                           ('[C2-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i4') &
#                           ('[C2-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i7'))) &
# ((! 'CONF_C3[0]') -> (    ('[C3-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i2') &
#                           ('[C3-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i5') &
#                           ('[C3-TMR_V111_A].abstr.o0' <-> '[C4-TMR_V111_A].concr.i8'))))