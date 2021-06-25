import fractions

from rel_tools import RelTools
from pysmt.optimization.goal import MinimizationGoal
import time
from approch import Hybrid, Enumerative, Symbolic

class Dse:
    def __init__(self, graph):
        self._graph = graph

    def optimize(self, benchmark=None, approch="symbolic"):
            if approch == "symbolic":
                appr = Symbolic(self._graph)
                cost, cost_formula = appr.extract_cost()
                rel, rel_formula = appr.extract_rel()
            elif approch == "hybrid":
                appr = Hybrid(self._graph, cfg_encoding="BOOL")
                cost, cost_formula = appr.extract_cost()
                rel, rel_formula = appr.extract_rel()
                #rel, rel_formula = h.extract_rel(cfg_type="INT")
            else:
                appr = Enumerative(self._graph)
                cost, cost_formula = appr.extract_cost()
                rel, rel_formula = appr.extract_rel()
            rel_obj = MinimizationGoal(rel)
            cost_obj = MinimizationGoal(cost)
            with Optimizer(name="z3") as opt:
                opt.add_assertion(rel_formula)
                opt.add_assertion(cost_formula)
                time_start = time.perf_counter()
                res = opt.pareto_optimize([cost_obj, rel_obj])
                print("[Optimizer] Find Pareto points...")
                pareto_points = []
                counter = 0
                for model, r in res:
                    counter = counter + 1
                    print("Solution " + str(counter))
                    print("   Patterns:")
                    print("   " + str(appr.get_patterns(model)))
                    print("   Parameters:")
                    print("   Cost: " + str(r[0]) + ", F-prob: ", str(float(fractions.Fraction(r[1].serialize()))))
                    pareto_points.append((model, r))
                    print("[Optimizer] " + str(counter) + " pareto points found",
                          end="\r", flush=True)
                print("[Optimizer] Done!")
            if benchmark is not None: benchmark.optimization_time = time.perf_counter() - time_start
            return pareto_points

if __name__ == "__main__":
    import random
    from patterns import *
    import networkx as nx
    import plotly.express as px
    import pandas as pd

    random.seed(a=1, version=2)
    pt_lib1 = [TmrV111Spec([NonFuncParamas(random.uniform(0,0.1), random.randrange(20)),
                            NonFuncParamas(random.uniform(0,0.1), random.randrange(20)),
                            NonFuncParamas(random.uniform(0,0.1), random.randrange(20))],
                           NonFuncParamas(random.uniform(0,0.1), random.randrange(20)))
               ]
    pt_lib2 = [TmrV111Spec([NonFuncParamas(random.uniform(0, 0.1), random.randrange(20)),
                            NonFuncParamas(random.uniform(0, 0.1), random.randrange(20)),
                            NonFuncParamas(random.uniform(0, 0.1), random.randrange(20))],
                           NonFuncParamas(random.uniform(0, 0.1), random.randrange(20))),
               TmrV111Spec([NonFuncParamas(random.uniform(0, 0.1), random.randrange(20)),
                            NonFuncParamas(random.uniform(0, 0.1), random.randrange(20)),
                            NonFuncParamas(random.uniform(0, 0.1), random.randrange(20))],
                           NonFuncParamas(random.uniform(0, 0.1), random.randrange(20)))
               ]
    pt_lib3 = [TmrV111Spec(
                   [NonFuncParamas(0.03, 5), NonFuncParamas(0.03, 5), NonFuncParamas(0.03, 5)],
                   NonFuncParamas(0.01, 6)),
        TmrV123Spec(
            [NonFuncParamas(0.03, 5), NonFuncParamas(0.03, 5), NonFuncParamas(0.03, 5)],
            [NonFuncParamas(0.01, 6),NonFuncParamas(0.01, 6), NonFuncParamas(0.01, 6)])
               ]


    g = nx.DiGraph()
    g.add_nodes_from([  ("S1", {'type': 'SOURCE'}),
                        ("C1", {'type': 'COMP', 'pt_library': pt_lib3}),
                        ("C2", {'type': 'COMP', 'pt_library': pt_lib3}),
                        ("C3", {'type': 'COMP', 'pt_library': pt_lib3})
    ])
    g.add_edge('S1', 'C1')
    g.add_edge('C1', 'C2')
    g.add_edge('C2', 'C3')

    d = Dse(g)
    res = d.optimize(approch="hybrid")
    rels = []
    costs = []
    for model, r in res:
        rel = float(fractions.Fraction(r[1].serialize()))
        cost = float(fractions.Fraction(r[0].serialize()))
        rels.append(rel)
        costs.append(cost)
    df = pd.DataFrame(list(zip(rels, costs)),
                   columns =['Reliability', 'Cost'])
    sorted = df.sort_values(by=['Reliability'])
    fig = px.line(sorted, x="Reliability", y="Cost")
    fig.update_traces(mode='markers+lines')
    #fig.show()


#(((('CONF_C1[0]' ? ('rel_\'CONF_C1[0]\'-0' = rel_C1_F0-6) : ('rel_\'CONF_C1[0]\'-0' = rel_C1_F0-1)) &
# (rel_C1_F0-1 = ((p0_C1 * rel_C1_F1-5) + ((1.0 - p0_C1) * rel_C1_F1-2))) &
# (rel_C1_F1-2 = ((p1_C1 * rel_C1_F2-4) + ((1.0 - p1_C1) * rel_C1_F3-3))) &
# (rel_C1_F3-3 = ((p3_C1 * 1))) &
# (rel_FALSE--2 = 0.0) & (rel_TRUE--1 = 1.0) &
# (rel_C1_F2-4 = ((p2_C1 * 1) + ((1.0 - p2_C1) * rel_C1_F3-3))) &
# (rel_C1_F1-5 = ((p1_C1 * 1) + ((1.0 - p1_C1) * rel_C1_F2-4))) &
# (rel_C1_F0-6 = ((p0_C1 * rel_C1_F1-12) + ((1.0 - p0_C1) * rel_C1_F1-7))) &////
# (rel_C1_F1-7 = ((p1_C1 * rel_C1_F2-11) + ((1.0 - p1_C1) * rel_C1_F3-8))) &///
# (rel_C1_F3-8 = ((p3_C1 * 1) + ((1.0 - p3_C1) * rel_C1_F4-9))) &////
# (rel_C1_F4-9 = ((p4_C1 * 1) + ((1.0 - p4_C1) * rel_C1_F5-10))) & ///
# (rel_C1_F2-11 = ((p2_C1 * 1) + ((1.0 - p2_C1) * rel_C1_F3-8))) & ///
# (rel_C1_F1-12 = ((p1_C1 * 1) + ((1.0 - p1_C1) * rel_C1_F2-11)))) &///
# (Rel = 'rel_\'CONF_C1[0]\'-0')) & (! False) &
#
#
# (((! 'CONF_C1[0]') -> (p0_C1 = 1080863910568919/36028797018963968)) & ((! 'CONF_C1[0]') -> (p1_C1 = 1080863910568919/36028797018963968)) & ((! 'CONF_C1[0]') -> (p2_C1 = 1080863910568919/36028797018963968)) & ((! 'CONF_C1[0]') -> (p3_C1 = 5764607523034235/576460752303423488)) & ('CONF_C1[0]' -> (p0_C1 = 1080863910568919/36028797018963968)) & ('CONF_C1[0]' -> (p1_C1 = 1080863910568919/36028797018963968)) & ('CONF_C1[0]' -> (p2_C1 = 1080863910568919/36028797018963968)) & ('CONF_C1[0]' -> (p3_C1 = 5764607523034235/576460752303423488)) & ('CONF_C1[0]' -> (p4_C1 = 5764607523034235/576460752303423488)) & ('CONF_C1[0]' -> (p5_C1 = 5764607523034235/576460752303423488))))
