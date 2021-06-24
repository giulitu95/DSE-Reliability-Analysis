import itertools
from patterns import *
import networkx as nx
import copy
import random
from rel_tools import RelTools
from tqdm import tqdm

class Enumerative:
    # TODO: it works only with compatible patterns!
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
        self._cost = Symbol("COST", REAL)

    def extract_cost(self):
        enum_cost = []
        for idx, combination in enumerate(itertools.product(*self._ptlibs)):
            comb = [*combination][0]
            cost = 0
            for params in comb.param_list:
                cost = cost + params.cost
            enum_cost.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._cost, Real(cost))))
        return self._cost, And(And(enum_cost), LT(self._cfg_id, Int(self._n_cfg)))

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
        return self._rel, And(And(enum_rel), LT(self._cfg_id, Int(self._n_cfg)))


class Hybrid:
    def __init__(self, graph):
        self._graph = graph
        self._rel = Symbol("R", REAL)
        self._cost = Symbol("COST", REAL)
        self._n_cfg = 1
        self.r = RelTools(self._graph)
        # Prepare list of libraries: [[lib1], [lib2], ...]
        for node in self._graph.nodes:
            if self._graph.nodes[node]["type"] == "COMP":
                lib = self._graph.nodes[node]["pt_library"]
                self._n_cfg = self._n_cfg * len(lib)  # Number of elements in the cartesiona product
                print(self._n_cfg)
        self._cfg_id = Symbol("cfg", INT)

    def __gen_cfg(self, node2conf2pt):
        cfgs_node= []
        for node, conf2pt in node2conf2pt.items():
            cfgs_node.append(list(conf2pt.keys()))
        for idx, combination in enumerate(itertools.product(*cfgs_node)):
            yield Equals(self._cfg_id, Int(idx)), And([*combination])

    def extract_cost(self):
        enum_cost = []
        pt_node= []
        for node, conf2pt in self.r.conf2pt.items():
            pt_node.append(list(conf2pt.values()))
        pbar = tqdm(total=self._n_cfg, desc="Finding Costs")
        for idx, combination in enumerate(itertools.product(*pt_node)):
            pbar.update(1)
            comb = [*combination]
            cost = 0
            for pt in comb:
                for params in pt.param_list:
                  cost = cost + params.cost
            enum_cost.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._cost, Real(cost))))
        pbar.close()
        return self._cost, And(And(enum_cost), LT(self._cfg_id, Int(self._n_cfg)))

    def extract_rel(self, cfg_type="INT"):
        rel_symbol, formula = self.r.extract_reliability_formula()
        enum_rel = []
        cfgs_node = []
        for node, conf2pt in self.r.conf2pt.items():
            cfgs_node.append(list(conf2pt.keys()))
        pbar = tqdm(total=self._n_cfg, desc="Finding Reliabilities")
        for idx, combination in enumerate(itertools.product(*cfgs_node)):
            pbar.update(1)
            bool_cfg = And([*combination])
            int_cfg = Equals(self._cfg_id, Int(idx))
            with Solver(name="z3") as solver:
                solver.add_assertion(formula)
                solver.add_assertion(bool_cfg)
                solver.add_assertion(self.r.prob_constr)
                solver.solve()
                rel = solver.get_value(rel_symbol)
            if cfg_type == "INT": enum_rel.append(Implies(int_cfg, Equals(self._rel, rel)))
            else: enum_rel.append(Implies(bool_cfg, Equals(self._rel, rel)))
        pbar.close()
        if cfg_type == "BOOL": res = self._rel, And(And(enum_rel), self.r.conf_formula)
        else: res = self._rel, And(And(enum_rel), LT(self._cfg_id, Int(self._n_cfg)))
        return res

'''random.seed(a=1, version=2)
pt_lib1 = [TmrV111Spec([NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20))],
                       NonFuncParamas(random.uniform(0,1), random.randrange(20))),
           TmrV111Spec([NonFuncParamas(random.uniform(0, 1),random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1),random.randrange(20))],
                       NonFuncParamas(random.uniform(0, 1),random.randrange(20))),
           TmrV111Spec([NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20))],
                       NonFuncParamas(random.uniform(0, 1), random.randrange(20)))
           ]
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
                    ("C2", {'type': 'COMP', 'pt_library': pt_lib1}),
                    ("C3", {'type': 'COMP', 'pt_library': pt_lib1}),
])
g.add_edge('S1', 'C1')
g.add_edge('C1', 'C2')
g.add_edge('C2', 'C3')


h = Hybrid(g)
h.extract_cost()
a, b = h.extract_rel(cfg_type="BOOL")
print(b.serialize())'''

