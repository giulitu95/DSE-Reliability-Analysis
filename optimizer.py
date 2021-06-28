import fractions

from rel_tools import RelTools
from pysmt.optimization.goal import MinimizationGoal
import time
import resource
from approch import Hybrid, Enumerative, Symbolic

class Dse:
    def __init__(self, graph):
        self._graph = graph

    def optimize(self, benchmark=None, approch="symbolic"):
            if approch == "symbolic":
                appr = Symbolic(self._graph)
                cost, cost_formula = appr.extract_cost()
                power, power_formula = appr.extract_power()
                size, size_formula = appr.extract_size()
                rel, rel_formula = appr.extract_rel()
            elif approch == "hybrid":
                appr = Hybrid(self._graph, cfg_encoding="BOOL")
                cost, cost_formula = appr.extract_cost()
                power, power_formula = appr.extract_power()
                size, size_formula = appr.extract_size()
                rel, rel_formula = appr.extract_rel()
                #rel, rel_formula = h.extract_rel(cfg_type="INT")
            else:
                appr = Enumerative(self._graph)
                cost, cost_formula = appr.extract_cost()
                power, power_formula = appr.extract_power()
                size, size_formula = appr.extract_size()
                rel, rel_formula = appr.extract_rel()

            #objective functions
            rel_obj = MinimizationGoal(rel)
            cost_obj = MinimizationGoal(cost)
            power_obj = MinimizationGoal(power)
            size_obj = MinimizationGoal(size)

            #print(rel_formula.serialize())
            #print(cost_formula.serialize())
            #print(power_formula.serialize())
            #print(size_formula.serialize())

            with Optimizer(name="z3") as opt:
                opt.add_assertion(rel_formula)
                opt.add_assertion(cost_formula)
                opt.add_assertion(power_formula)
                opt.add_assertion(size_formula)
                #Start timer
                time_start = time.perf_counter()
                res = opt.pareto_optimize([cost_obj, power_obj, size_obj, rel_obj])
                print("[Optimizer] Find Pareto points...")
                pareto_points = []
                counter = 0
                for model, r in res:
                    counter = counter + 1
                    print("Solution " + str(counter))
                    print("   Patterns:")
                    print("   " + str(appr.get_patterns(model)))
                    print("   Parameters:")
                    print("   Cost: " + str(r[0]) + ", Power " + str(r[1]) + ", Size: " + str(r[2]) + ", F-prob: ", str(float(fractions.Fraction(r[3].serialize()))))
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
    #from networkx.drawing.nx_agraph import write_dot, graphviz_layout
    #import matplotlib.pyplot as plt
    import plotly.express as px
    import pandas as pd

    '''
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
    '''

    # Pattern Libs
    pt_lib1 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 11, 20), NonFuncParamas(0.1, 10, 11, 20), NonFuncParamas(0.1, 10, 11, 20)],
                    [NonFuncParamas(0.1, 2, 4, 3), NonFuncParamas(0.1, 2, 4, 3), NonFuncParamas(0.1, 2, 4, 3)]),
        TmrV111Spec([NonFuncParamas(0.2, 10, 9, 16), NonFuncParamas(0.2, 10, 9, 16), NonFuncParamas(0.2, 11, 9, 16)],
                    NonFuncParamas(0.1, 2, 3, 3))
    ]
    pt_lib2 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 12, 22), NonFuncParamas(0.1, 10, 12, 22), NonFuncParamas(0.1, 10, 12, 22)],
                    [NonFuncParamas(0.1, 2, 3, 2), NonFuncParamas(0.1, 2, 3, 2), NonFuncParamas(0.1, 2, 3, 2)]),
        TmrV111Spec([NonFuncParamas(0.2, 11, 13, 17), NonFuncParamas(0.2, 11, 13, 17), NonFuncParamas(0.2, 11, 13, 17)],
                    NonFuncParamas(0.1, 4, 2, 3))
    ]
    pt_lib3 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 14, 21), NonFuncParamas(0.1, 10, 14, 21), NonFuncParamas(0.1, 10, 14, 21)],
                    [NonFuncParamas(0.1, 2, 3, 4), NonFuncParamas(0.1, 2, 3, 4), NonFuncParamas(0.1, 2, 3, 4)]),
        TmrV111Spec([NonFuncParamas(0.2, 11, 15, 16), NonFuncParamas(0.2, 11, 15, 16), NonFuncParamas(0.2, 11, 15, 16)],
                    NonFuncParamas(0.1, 2, 3, 3))
    ]
    pt_lib4 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 11, 19), NonFuncParamas(0.1, 10, 11, 19), NonFuncParamas(0.1, 10, 11, 19)],
                    [NonFuncParamas(0.1, 2, 3, 4), NonFuncParamas(0.1, 2, 3, 4), NonFuncParamas(0.1, 2, 3, 4)]),
        TmrV111Spec([NonFuncParamas(0.2, 11, 12, 15), NonFuncParamas(0.8, 11, 12, 15), NonFuncParamas(0.2, 11, 12, 15)],
                    NonFuncParamas(0.1, 2, 2, 5))
    ]

    pt_lib5 = [
        TmrV123Spec([NonFuncParamas(0.2, 11, 13, 21), NonFuncParamas(0.2, 11, 13, 21), NonFuncParamas(0.2, 11, 13, 21)],
                    [NonFuncParamas(0.1, 2, 4, 3), NonFuncParamas(0.1, 2, 4, 3), NonFuncParamas(0.1, 2, 4, 3)]),
        TmrV111Spec([NonFuncParamas(0.2, 11, 12, 16), NonFuncParamas(0.2, 11, 12, 16), NonFuncParamas(0.2, 11, 12, 16)],
                    NonFuncParamas(0.2, 2, 5, 4))
    ]
    pt_lib6 = [
        TmrV123Spec([NonFuncParamas(0.1, 12, 12, 18), NonFuncParamas(0.1, 12, 12, 18), NonFuncParamas(0.1, 12, 12, 18)],
                    [NonFuncParamas(0.1, 2, 3, 2), NonFuncParamas(0.1, 2, 3, 2), NonFuncParamas(0.1, 2, 3, 2)]),
        TmrV111Spec([NonFuncParamas(0.2, 12, 11, 14), NonFuncParamas(0.2, 12, 11, 14), NonFuncParamas(0.2, 12, 11, 14)],
                    NonFuncParamas(0.3, 3, 4, 3))
    ]

    G = nx.DiGraph()
    G.add_nodes_from([("S1", {'type': 'SOURCE'}),
                      ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                      ("C2", {'type': 'COMP', 'pt_library': pt_lib2}),
                      ("C3", {'type': 'COMP', 'pt_library': pt_lib3}),
                      ("C4", {'type': 'COMP', 'pt_library': pt_lib4}),
                      ("C5", {'type': 'COMP', 'pt_library': pt_lib5}),
                      ("C6", {'type': 'COMP', 'pt_library': pt_lib6})
                      ])
    #G.add_edge('S1', 'C1')
    #G.add_edge('C1', 'C2')
    #G.add_edge('C2', 'C3')
    G.add_edge('S1', 'C1')
    G.add_edge('S1', 'C2')
    G.add_edge('C1', 'C3')
    G.add_edge('C1', 'C4')
    G.add_edge('C2', 'C4')
    G.add_edge('C2', 'C5')
    G.add_edge('C3', 'C6')
    G.add_edge('C4', 'C6')
    G.add_edge('C5', 'C6')

    ##plot architecture graph
    #nx.draw(g)
    #plt.show()
    #plt.figure(1)
    #pos = nx.spring_layout(g)
    #nx.draw_networkx_nodes(g, pos, node_color='blue', node_shape='s', node_size=2000)
    #nx.draw_networkx_edges(g, pos, edgelist=g.edges(), arrows=True)
    #nx.draw_networkx_labels(g, pos, font_size=10, font_color="white")
    #plt.ion()
    #plt.show()

    # Start timer
    #time_start = time.perf_counter()

    #Optimization
    d = Dse(G)
    res = d.optimize(approch="hybrid")

    # calculate time
    #time_elapsed = (time.perf_counter() - time_start)
    # calculate memory usage
    #memMb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0

    rels = []
    costs = []
    powers = []
    sizes = []

    for model, r in res:
        rel = float(fractions.Fraction(r[3].serialize()))
        size = float(fractions.Fraction(r[2].serialize()))
        power = float(fractions.Fraction(r[1].serialize()))
        cost = float(fractions.Fraction(r[0].serialize()))
        rels.append(rel)
        costs.append(cost)
        powers.append(power)
        sizes.append(size)

    df = pd.DataFrame(list(zip(rels, costs, powers, sizes)),
                   columns =['Reliability', 'Cost', 'Size', 'Power'])
    sorted = df.sort_values(by=['Reliability'])
    #fig = px.line(sorted, x="Reliability", y="Cost")
    #fig.update_traces(mode='markers+lines')
    #fig.show()


#Example plot: Pareto 2D plot of the paper (2 objectives)
fig = px.line(
    x=[0.673964, 0.692971, 0.705806, 0.722956, 0.746054, 0.767727, 0.782202, 0.854541], y=[225.0, 222.0, 221.0, 218.0, 217.0, 215.0, 214.0, 213.0]
    #title="Pareto front"
)
fig.update_traces(line=dict(color="Blue", width=3))
fig.update_traces(mode='markers+lines', marker=dict(size=14, line=dict(color="DarkSlateGrey", width=3)))

fig.update_xaxes(title_text='Reliability', title_font=dict(size=24, family='Courier', color='Blue'))
fig.update_yaxes(title_text='Cost', title_font=dict(size=24, family='Courier', color='Blue'))

fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightPink')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightPink')

fig.show()

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
