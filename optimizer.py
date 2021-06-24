import fractions

from rel_tools import RelTools
from pysmt.optimization.goal import MinimizationGoal
import time
from approch import Hybrid, Enumerative

class Dse:
    def __init__(self, graph):
        self._graph = graph

    def __extract_cost(self, r):
        cost_constr = []
        node_costs = []
        for nx_node, an in r.nxnode2archnode.items():
            node_cost = Symbol(nx_node + "_COST", REAL)
            node_costs.append(node_cost)
            for cfg, pt in an.conf2pt.items():
                pt_cost = 0
                for params in pt.param_list:
                    pt_cost = pt_cost + params.cost
                cost_constr.append(Implies(cfg, Equals(node_cost, Real(pt_cost))))
        cost_assignments = And(cost_constr)
        cost = Symbol("cost", REAL)
        return cost, And(Equals(cost, Plus(node_costs)), cost_assignments)

    def optimize(self, benchmark=None, approch="symbolic"):
        with Optimizer(name="z3") as opt:
            if approch == "symbolic":
                r = RelTools(self._graph)
                cost, cost_formula = self.__extract_cost(r)
                rel, rel_formula = r.extract_reliability_formula()
                opt.add_assertion(r.prob_constr) # only in this case we need prob constraints
            elif approch == "hybrid":
                h = Hybrid(self._graph, cfg_encoding="BOOL")
                cost, cost_formula = h.extract_cost()
                rel, rel_formula = h.extract_rel()
                #rel, rel_formula = h.extract_rel(cfg_type="INT")
            else:
                e = Enumerative(self._graph)
                cost, cost_formula = e.extract_cost()
                rel, rel_formula = e.extract_rel()
            rel_obj = MinimizationGoal(rel)
            cost_obj = MinimizationGoal(cost)
            opt.add_assertion(rel_formula)
            opt.add_assertion(cost_formula)
            time_start = time.perf_counter()
            res = opt.pareto_optimize([cost_obj, rel_obj])
            print("[Optimizer] Find Pareto points...")
            pareto_points = []
            counter = 0
            for model, r in res:
                pareto_points.append((model, r))
                counter = counter + 1
                print("[Optimizer] " + str(counter) + " pareto points found",
                      end="\r", flush=True)
            print("[Optimizer] Done!")
            if benchmark is not None: benchmark.optimization_time = time.perf_counter() - time_start
            return pareto_points


import random
from patterns import *
import networkx as nx

random.seed(a=1, version=2)
pt_lib1 = [TmrV111Spec([NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20))],
                       NonFuncParamas(random.uniform(0,1), random.randrange(20))),
           TmrV111Spec([NonFuncParamas(random.uniform(0, 1),random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1),random.randrange(20))],
                       NonFuncParamas(random.uniform(0, 1),random.randrange(20)))
           ]

g = nx.DiGraph()
g.add_nodes_from([  ("S1", {'type': 'SOURCE'}),
                    ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                    ("C2", {'type': 'COMP', 'pt_library': pt_lib1}),
                    ("C3", {'type': 'COMP', 'pt_library': pt_lib1}),
])
g.add_edge('S1', 'C1')
g.add_edge('C1', 'C2')
g.add_edge('C2', 'C3')


d = Dse(g)
res = d.optimize(approch="hybrid")
for model, r in res:
    rel = float(fractions.Fraction(r[1].serialize()))
    cost = float(fractions.Fraction(r[0].serialize()))
    print(r[0], rel)