if __name__ == "__main__":
    import random
    from patterns import *
    import fractions
    import networkx as nx
    import plotly.express as px
    import pandas as pd
    from optimizer import Dse
    import os
    import time
    import resource
    os.chdir("../")

    # Pattern Libs
    pt_lib1 = [
        TmrV123Spec([NonFuncParamas(0.1, 10, 11, 20), NonFuncParamas(0.1, 10, 11, 20), NonFuncParamas(0.1, 10, 11, 20)],
                    [NonFuncParamas(0.1, 2, 4, 3), NonFuncParamas(0.1, 2, 4, 3), NonFuncParamas(0.1, 2, 4, 3)]),
        Xooy3oo4Spec([NonFuncParamas(0.2, 10, 9, 16), NonFuncParamas(0.2, 10, 9, 16), NonFuncParamas(0.2, 11, 9, 16),
                      NonFuncParamas(0.2, 11, 9, 16)],
                     NonFuncParamas(0.1, 2, 3, 3)),
        Xooy3oo4Spec([NonFuncParamas(0.2, 10, 9, 16), NonFuncParamas(0.2, 10, 9, 16), NonFuncParamas(0.2, 11, 9, 16), NonFuncParamas(0.2, 11, 9, 16)],
                    NonFuncParamas(0.1, 2, 3, 3))
    ]
    pt_lib2 = [
        TmrV111Spec([NonFuncParamas(0.2, 11, 13, 17), NonFuncParamas(0.2, 11, 13, 17), NonFuncParamas(0.2, 11, 13, 17)],
                    NonFuncParamas(0.1, 4, 2, 3)),
        Xooy3oo4Spec([NonFuncParamas(0.1, 10, 9, 16), NonFuncParamas(0.1, 10, 9, 16), NonFuncParamas(0.1, 11, 9, 16), NonFuncParamas(0.1, 11, 9, 16)],
                    NonFuncParamas(0.1, 2, 3, 3)),
        Xooy3oo4Spec([NonFuncParamas(0.2, 10, 9, 16), NonFuncParamas(0.2, 10, 9, 16), NonFuncParamas(0.2, 11, 9, 16),
                      NonFuncParamas(0.2, 11, 9, 16)],
                     NonFuncParamas(0.1, 2, 3, 3))
    ]
    pt_lib3 = [
        Xooy3oo4Spec([NonFuncParamas(0.2, 10, 9, 15), NonFuncParamas(0.2, 10, 9, 15), NonFuncParamas(0.2, 11, 9, 15),
                      NonFuncParamas(0.2, 11, 9, 15)],
                     NonFuncParamas(0.1, 2, 3, 3)),
        Xooy3oo4Spec([NonFuncParamas(0.1, 15, 9, 16), NonFuncParamas(0.1, 15, 9, 16), NonFuncParamas(0.1, 15, 9, 16), NonFuncParamas(0.1, 15, 9, 16)],
                    NonFuncParamas(0.1, 2, 3, 3)),
        Xooy3oo4Spec([NonFuncParamas(0.3, 10, 9, 16), NonFuncParamas(0.3, 10, 9, 16), NonFuncParamas(0.3, 11, 9, 16),
                      NonFuncParamas(0.3, 11, 9, 16)],
                     NonFuncParamas(0.2, 2, 3, 3))
    ]

    pt_lib4 = [
        Xooy3oo4Spec([NonFuncParamas(0.3, 15, 12, 15), NonFuncParamas(0.3, 15, 12, 15), NonFuncParamas(0.3, 15, 12, 15),
                      NonFuncParamas(0.3, 15, 12, 15)],
                     NonFuncParamas(0.1, 2, 3, 3)),
        Xooy3oo4Spec([NonFuncParamas(0.2, 12, 9, 16), NonFuncParamas(0.2, 12, 9, 16), NonFuncParamas(0.2, 12, 9, 16),
                      NonFuncParamas(0.2, 12, 9, 16)],
                     NonFuncParamas(0.1, 2, 3, 3)),
        Xooy3oo4Spec([NonFuncParamas(0.3, 15, 9, 16), NonFuncParamas(0.3, 15, 9, 16), NonFuncParamas(0.3, 15, 9, 16), NonFuncParamas(0.3, 15, 9, 16)],
                    NonFuncParamas(0.1, 2, 3, 3))
    ]

    G = nx.DiGraph()
    G.add_nodes_from([("S1", {'type': 'SOURCE'}),
                      ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                      ("C2", {'type': 'COMP', 'pt_library': pt_lib2}),
                      ("C3", {'type': 'COMP', 'pt_library': pt_lib3}),
                      ("C4", {'type': 'COMP', 'pt_library': pt_lib4})
                      ])
    G.add_edge('S1', 'C1')
    G.add_edge('C1', 'C2')
    G.add_edge('C2', 'C3')
    G.add_edge('C3', 'C4')


    # Start timer
    time_start = time.perf_counter()

    #Optimization
    d = Dse(G)
    res = d.optimize(approch="hybrid")

    # calculate time
    time_elapsed = (time.perf_counter() - time_start)
    # calculate memory usage
    memMb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0

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
    print(sorted)
