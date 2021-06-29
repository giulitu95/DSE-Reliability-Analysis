if __name__ == "__main__":
    import random
    from patterns import *
    import fractions
    import networkx as nx
    #from networkx.drawing.nx_agraph import write_dot, graphviz_layout
    #import matplotlib.pyplot as plt
    import plotly.express as px
    import pandas as pd
    from optimizer import Dse
    import os
    os.chdir("../")

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


    #Example plot: Pareto 3d plot (3 objectives)
    from mpl_toolkits import mplot3d
    from mpl_toolkits.mplot3d import axes3d
    import numpy as np
    import matplotlib.pyplot as plt

    fig = plt.figure()
    #R
    X = np.array([0.673964, 0.684499, 0.692971, 0.705806, 0.708439, 0.712695, 0.722956, 0.736914, 0.746054,  0.758847,  0.767727,  0.779429,  0.782202,  0.793175, 0.837494, 0.841752, 0.850627, 0.854541])
    #C
    Y = np.array([225.0, 226.0, 222.0, 221.0, 223.0, 221.0, 218.0, 219.0, 217.0, 218.0, 215.0, 216.0, 214.0, 215.0, 215.0, 214.0, 214.0, 213.0])
    #P
    Z = np.array([279.0, 275.0, 264.0, 269.0, 260.0, 261.0, 254.0, 250.0, 251.0, 247.0, 246.0, 242.0, 243.0, 239.0, 238.0, 242.0, 235.0, 239.0])
    #
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    my_cmap = plt.get_cmap('hot')
    trisurf = ax.plot_trisurf(X, Y, Z,
                         cmap = my_cmap,
                         linewidth = 0.2,
                         antialiased = True,
                         edgecolor = 'grey')
    fig.colorbar(trisurf, ax = ax, shrink = 0.5, aspect = 5)
    ax.set_title('Pareto of three functions')
    # Adding labels
    ax.set_xlabel('Reliability', fontweight ='bold')
    ax.set_ylabel('Cost', fontweight ='bold')
    ax.set_zlabel('Power Consumption', fontweight ='bold')
    plt.show()
