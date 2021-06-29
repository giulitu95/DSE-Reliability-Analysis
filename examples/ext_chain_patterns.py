import pandas as pd
from benchmark import Benchmark
from rel_tools import RelTools
import networkx as nx
import csv
import random
from params import NonFuncParamas
from patterns import TmrV111Spec, PlainSpec, TmrV123Spec
import os
import plotly.express as px
os.chdir("../")

def test_chain(file_name, pt_lib, max_len = 100):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(Benchmark.get_header() + ["len"]) # header
        for len in range(2, max_len):
            benchmark = Benchmark()
            print("~"*10 + " " + str(len) + " len chain " + "~"*10)
            graph = nx.DiGraph()
            graph.add_nodes_from([("S", {'type': 'SOURCE'})])
            nodes = [("C" + str(idx), {'type': 'COMP', 'pt_library': pt_lib}) for idx in range(len)]
            graph.add_nodes_from(nodes)
            edges = [("C" + str(idx), "C" + str(idx + 1)) for idx in range(len - 1)]
            edges.append(("S", "C0"))
            graph.add_edges_from(edges)
            r = RelTools(graph)
            r.extract_reliability_formula(benchmark=benchmark)
            writer.writerow(benchmark.get_values() + [len])


if __name__ == "__main__":
    tmr_v111 = TmrV111Spec( [   NonFuncParamas(random.uniform(0,0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20))],
                            NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20)))
    tmr_v123 = TmrV123Spec([    NonFuncParamas(random.uniform(0,0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20))],
                           [    NonFuncParamas(random.uniform(0, 0.01), random.randrange(20), random.randrange(20),random.randrange(20)),
                                NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20))]
                           )
    plain = PlainSpec(NonFuncParamas(random.uniform(0,0.01), random.randrange(20), random.randrange(20), random.randrange(20)))
    v111_filename = "benchmarks/extraction-v111-chain.csv"
    v123_filename = "benchmarks/extraction-v123-chain.csv"
    plain_filename = "benchmarks/extraction-plain-chain.csv"
    if not os.path.isfile(v111_filename):
        test_chain(v111_filename, [tmr_v111])
    if not os.path.isfile(plain_filename):
        test_chain(plain_filename, [plain])
    if not os.path.isfile(v123_filename):
        test_chain(v123_filename, [tmr_v123])

    v111_df = pd.read_csv(v111_filename)
    v123_df = pd.read_csv(v123_filename)
    plain_df = pd.read_csv(plain_filename)

    res_df = []
    tmp_v111_df = v111_df[['len', 'total_ext_time']].copy()
    tmp_v111_df['pattern'] = "TMR-V111"
    res_df.append(tmp_v111_df)

    tmp_v123_df = v123_df[['len', 'total_ext_time']].copy()
    tmp_v123_df['pattern'] = "TMR-V123"
    res_df.append(tmp_v123_df)

    tmp_plain_df = plain_df[['len', 'total_ext_time']].copy()
    tmp_plain_df['pattern'] = "PLAIN"
    res_df.append(tmp_plain_df)

    res = pd.concat(res_df, axis=0)
    fig = px.line(res, x="len",
                  y="total_ext_time",
                  color='pattern',
                  labels={"pattern": "Patterns", "total_ext_time": "Time (s)", "len": "Chain length"},
                  title="Multiple patterns comparison")
    fig.show()