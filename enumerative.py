import itertools
from patterns import *
import networkx as nx
import copy
import random
from rel_tools import RelTools


class Enumerative:
    def __init__(self, graph):
        self._graph = graph
        self._n_cfg = 1
        self._ptlibs = []
        # Prepare list of libraries: [[lib1], [lib2], ...]
        for node in self._graph.nodes:
            if self._graph.nodes[node]["type"] == "COMP":
                lib = self._graph.nodes[node]["pt_library"]
                self._n_cfg = self._n_cfg * len(lib)  # Number of elements in the cartesiona product
                self._ptlibs.append(lib)
        #self._cfg_bv = Symbol("cfg", BVType(math.ceil(math.log(n_cfg, 2))))
        self._cfg_id = Symbol("cfg", INT)
        self._rel = Symbol("R", REAL)

    def extract_rel(self):
        # Perform the cartesian product to find all combinations and create the graph
        enum_rel = []
        for idx, combination in enumerate(itertools.product(*self._ptlibs)):
            print("[Enumerative] ~~~ " + str(idx+1) + "th combination out of " + str(self._n_cfg) + " ~~~")
            comb = [*combination]
            # make a copy of the graph changing the patterns library for each component
            ng = copy.deepcopy(self._graph)
            for node in ng.nodes:
                if ng.nodes[node]["type"]  == "COMP":
                    ng.nodes[node]["pt_library"] = [comb.pop(0)]
            r = RelTools(ng)
            rel_symbol, formula = r.extract_reliability_formula()
            # Find reliability value for this combination
            with Solver(name="z3") as solver:
                solver.add_assertion(formula)
                solver.add_assertion(r.prob_constr)
                solver.solve()
                rel = solver.get_value(rel_symbol)
            enum_rel.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._rel, rel)))
        return And(And(enum_rel), LT(self._cfg_id, Int(self._n_cfg)))


'''random.seed(a=1, version=2)
pt_lib1 = [TmrV111Spec([NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20))],
                       NonFuncParamas(random.uniform(0,1), random.randrange(20))),
           TmrV111Spec([NonFuncParamas(random.uniform(0, 1),random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1),random.randrange(20))],
                       NonFuncParamas(random.uniform(0, 1),random.randrange(20)))]
pt_lib2 = [TmrV111Spec([NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20))],
                       NonFuncParamas(random.uniform(0,1), random.randrange(20))),
           TmrV111Spec([NonFuncParamas(random.uniform(0, 1),random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1),random.randrange(20))],
                       NonFuncParamas(random.uniform(0, 1),random.randrange(20)))]

g = nx.DiGraph()
g.add_nodes_from([  ("S1", {'type': 'SOURCE'}),
                    ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                    ("C2", {'type': 'COMP', 'pt_library': pt_lib2}),
])
g.add_edge('S1', 'C1')
g.add_edge('C1', 'C2')

e = Enumerative(g)
f = e.extract_rel()
print(f)'''
