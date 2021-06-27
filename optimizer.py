import fractions

from rel_tools import RelTools
import matplotlib.pyplot as plt
from pysmt.optimization.goal import MinimizationGoal
import time
import resource
from approch import Hybrid, Enumerative, Symbolic

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

    def __extract_power(self, r):
        power_constr = []
        node_powers = []
        for nx_node, an in r.nxnode2archnode.items():
            node_power = Symbol(nx_node + "_POWER", REAL)
            node_powers.append(node_power)
            for cfg, pt in an.conf2pt.items():
                pt_power = 0
                for params in pt.param_list:
                    pt_power = pt_power + params.power
                power_constr.append(Implies(cfg, Equals(node_power, Real(pt_power))))
        power_assignments = And(power_constr)
        power = Symbol("power", REAL)
        return power, And(Equals(power, Plus(node_powers)), power_assignments)
    
    def optimize(self, benchmark=None, approch="symbolic"):
            #three approaches available: numeric, symbolic, hybrid
            if approch == "symbolic":
                s = Symbolic(self._graph)
                cost, cost_formula = s.extract_cost()
                power, power_formula = s.extract_power()
                rel, rel_formula = s.extract_rel()
            elif approch == "hybrid":
                h = Hybrid(self._graph, cfg_encoding="BOOL")
                cost, cost_formula = h.extract_cost()
                power, power_formula = h.extract_power()
                rel, rel_formula = h.extract_rel()
                #rel, rel_formula = h.extract_rel(cfg_type="INT")
            else:
                e = Enumerative(self._graph)
                cost, cost_formula = e.extract_cost()
                power, power_formula = e.extract_power()
                rel, rel_formula = e.extract_rel()
            
            rel_obj = MinimizationGoal(rel)
            cost_obj = MinimizationGoal(cost)
            power_obj = MinimizationGoal(power)
            
            print(rel_formula.serialize())
            print(cost_formula.serialize())
            print(power_formula.serialize())
            
            with Optimizer(name="z3") as opt:
                opt.add_assertion(rel_formula)
                opt.add_assertion(cost_formula)
                opt.add_assertion(power_formula)                
                time_start = time.perf_counter()
                res = opt.pareto_optimize([cost_obj, power_obj, rel_obj])
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

if __name__ == "__main__":
    import random
    from patterns import *
    import networkx as nx
    #from networkx.drawing.nx_agraph import write_dot, graphviz_layout
    #import matplotlib.pyplot as plt
    import plotly.express as px
    import pandas as pd

    '''
    #random.seed(a=1, version=2)
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
                        ("C2", {'type': 'COMP', 'pt_library': pt_lib3})
    ])
    g.add_edge('S1', 'C1')
    g.add_edge('C1', 'C2')
    '''

    pt_lib1 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 11), NonFuncParamas(0.1, 10, 11), NonFuncParamas(0.1, 10, 11)],
                    [NonFuncParamas(0.1, 2, 4), NonFuncParamas(0.1, 2, 4), NonFuncParamas(0.1, 2, 4)]),
        TmrV111Spec([NonFuncParamas(0.2, 10, 9), NonFuncParamas(0.2, 10, 9), NonFuncParamas(0.2, 11, 9)],
                    NonFuncParamas(0.1, 2, 3))
    ]
    pt_lib2 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 12), NonFuncParamas(0.1, 10, 12), NonFuncParamas(0.1, 10, 12)],
                    [NonFuncParamas(0.1, 2, 3), NonFuncParamas(0.1, 2, 3), NonFuncParamas(0.1, 2, 3)]),
        TmrV111Spec([NonFuncParamas(0.2, 11, 13), NonFuncParamas(0.2, 11, 13), NonFuncParamas(0.2, 11, 13)],
                    NonFuncParamas(0.1, 4, 2))
    ]
    pt_lib3 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 14), NonFuncParamas(0.1, 10, 14), NonFuncParamas(0.1, 10, 14)],
                    [NonFuncParamas(0.1, 2, 3), NonFuncParamas(0.1, 2, 3), NonFuncParamas(0.1, 2, 3)]),
        TmrV111Spec([NonFuncParamas(0.2, 11, 15), NonFuncParamas(0.2, 11, 15), NonFuncParamas(0.2, 11, 15)],
                    NonFuncParamas(0.1, 2, 3))
    ]
    pt_lib4 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 11), NonFuncParamas(0.1, 10, 11), NonFuncParamas(0.1, 10, 11)],
                    [NonFuncParamas(0.1, 2, 3), NonFuncParamas(0.1, 2, 3), NonFuncParamas(0.1, 2, 3)]),
        TmrV111Spec([NonFuncParamas(0.2, 11, 12), NonFuncParamas(0.8, 11, 12), NonFuncParamas(0.2, 11, 12)],
                    NonFuncParamas(0.1, 2, 2))
    ]

    pt_lib5 = [
        TmrV123Spec([NonFuncParamas(0.2, 11, 13), NonFuncParamas(0.2, 11, 13), NonFuncParamas(0.2, 11, 13)],
                    [NonFuncParamas(0.1, 2, 4), NonFuncParamas(0.1, 2, 4), NonFuncParamas(0.1, 2, 4)]),
        TmrV111Spec([NonFuncParamas(0.2, 11, 12), NonFuncParamas(0.2, 11, 12), NonFuncParamas(0.2, 11, 12)],
                    NonFuncParamas(0.2, 2, 5))
    ]
    pt_lib6 = [
        TmrV123Spec([NonFuncParamas(0.1, 12, 12), NonFuncParamas(0.1, 12, 12), NonFuncParamas(0.1, 12, 12)],
                    [NonFuncParamas(0.1, 2, 3), NonFuncParamas(0.1, 2, 3), NonFuncParamas(0.1, 2, 3)]),
        TmrV111Spec([NonFuncParamas(0.2, 12, 11), NonFuncParamas(0.2, 12, 11), NonFuncParamas(0.2, 12, 11)],
                    NonFuncParamas(0.3, 3, 4))
    ]

    g = nx.DiGraph()
    g.add_nodes_from([("S1", {'type': 'SOURCE'}),
                      ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                      ("C2", {'type': 'COMP', 'pt_library': pt_lib2}),
                      ("C3", {'type': 'COMP', 'pt_library': pt_lib3}),
                      ("C4", {'type': 'COMP', 'pt_library': pt_lib4}),
                      ("C5", {'type': 'COMP', 'pt_library': pt_lib5}),
                      ("C6", {'type': 'COMP', 'pt_library': pt_lib6})
                      ])

    g.add_edge('S1', 'C1')
    g.add_edge('S1', 'C2')
    g.add_edge('C1', 'C3')
    g.add_edge('C1', 'C4')
    g.add_edge('C2', 'C4')
    g.add_edge('C2', 'C5')
    g.add_edge('C3', 'C6')
    g.add_edge('C4', 'C6')
    g.add_edge('C5', 'C6')

    ##plot graph
    #nx.draw(g)
    #plt.show()
    #plt.figure(1)
    #pos = nx.spring_layout(g)
    #nx.draw_networkx_nodes(g, pos, node_color='blue', node_shape='s', node_size=2000)
    #nx.draw_networkx_edges(g, pos, edgelist=g.edges(), arrows=True)
    #nx.draw_networkx_labels(g, pos, font_size=10, font_color="white")
    #plt.ion()
    #plt.show()

    #start time
    time_start = time.perf_counter()

    d = Dse(g)
    res = d.optimize(approch="hybrid")

    #calculate time
    time_elapsed = (time.perf_counter() - time_start)
    #calculate memory usage
    memMb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0/1024.0

    rels = []
    costs = []
    powers = []
    
    for model, r in res:
        rel = float(fractions.Fraction(r[2].serialize()))
        power = float(fractions.Fraction(r[1].serialize()))
        cost = float(fractions.Fraction(r[0].serialize()))
        rels.append(rel)
        costs.append(cost)
        powers.append(power)
        print(cost, power, rel)
        df = pd.DataFrame(list(zip(rels, costs, powers)), columns =['Reliability', 'Cost', 'Power Consumption'])
        sorted = df.sort_values(by=['Reliability'])
        print(sorted)

#    print(r[0], rel)
#    df = pd.DataFrame(list(zip(rels, costs)),
#                   columns =['Reliability', 'Cost'])
#    sorted = df.sort_values(by=['Reliability'])

#    print(sorted)
#    fig = px.line(sorted, x="Reliability", y="Cost")
#    fig.update_traces(mode='markers+lines')
#    fig.show()


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
