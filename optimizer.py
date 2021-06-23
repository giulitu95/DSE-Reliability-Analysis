import fractions

from rel_tools import RelTools
from pysmt.shortcuts import *
from pysmt.optimization.goal import MinimizationGoal
from pysmt.logics import Logic
import time
class Dse:
    def __init__(self, graph):
        self._r = RelTools(graph)

    def __extract_cost_formula(self):
        cost_constr = []
        node_costs = []
        for nx_node, an in self._r.nxnode2archnode.items():
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

    def optimize(self, benchmark=None):
        cost, cost_formula = self.__extract_cost_formula()
        rel, rel_formula = self._r.extract_reliability_formula()
        cost_obj = MinimizationGoal(cost)
        rel_obj = MinimizationGoal(rel)

        with Optimizer(name="z3") as opt:
            opt.add_assertion(self._r.conf_formula)
            opt.add_assertion(self._r.prob_constr)
            opt.add_assertion(self._r.compatibility_constr)
            opt.add_assertion(cost_formula)
            opt.add_assertion(rel_formula)
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

'''
import networkx as nx
from patterns.pt_spec import *
pt_lib1 = [
    TmrV111Spec([NonFuncParamas(0.9, 1), NonFuncParamas(0.9, 2), NonFuncParamas(0.9, 3) ],
                NonFuncParamas(0.9, 5)),
    TmrV111Spec([NonFuncParamas(0.1,3), NonFuncParamas(0.3,5), NonFuncParamas(0.03,3)],
                NonFuncParamas(0.2,6)),
    TmrV111Spec([NonFuncParamas(0.1, 6), NonFuncParamas(0.3, 5), NonFuncParamas(0.03, 3)],
                NonFuncParamas(0.1, 6)),
    TmrV111Spec([NonFuncParamas(0.7,3), NonFuncParamas(0.3,1), NonFuncParamas(0.03,3)],
                NonFuncParamas(0.2,6))
]


# (A & B) | C: 110 - 111 - 001 - 011 - 101 10,01,11
g = nx.DiGraph()
g.add_nodes_from([  ("S1", {'type': 'SOURCE'}),
                    ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                    ("C2", {'type': 'COMP', 'pt_library': pt_lib1})
])
g.add_edge('S1', 'C1')
g.add_edge('C1', 'C2')


o = Dse(g)
res = o.optimize()

for oname in get_env().factory.all_solvers(logic=QF_NRA): print(oname)
for oname in get_env().factory.all_optimizers(logic=QF_NRA): print(oname)
'''