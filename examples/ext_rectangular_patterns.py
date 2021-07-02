from params import NonFuncParamas
from patterns import TmrV111Spec, TmrV123Spec, PlainSpec
import csv
import pandas as pd
import random
import os
import plotly.express as px
import networkx as nx
from benchmark import Benchmark
from rel_tools import RelTools
os.chdir("../")

def test_rectangle(file_name, pt_lib, max_len = 50):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(Benchmark.get_header() + ["len"]) # header
        for len in range(2, max_len):
            benchmark = Benchmark()
            print("~"*10 + " " + str(len) + " len chain " + "~"*10)
            graph = nx.DiGraph()
            graph.add_nodes_from([("S0_A", {'type': 'SOURCE'}), ("S0_B", {'type': 'SOURCE'})])
            nodes = []
            edges = []
            nodes.append(("C" + str(len - 1) + "_A", {'type': 'COMP', 'pt_library': pt_lib}))
            nodes.append(("C" + str(len - 1) + "_B", {'type': 'COMP', 'pt_library': pt_lib}))
            for idx in reversed(range(len - 1)):
                nodes.append(("C" + str(idx) + "_A", {'type': 'COMP', 'pt_library': pt_lib}))
                nodes.append(("C" + str(idx) + "_B", {'type': 'COMP', 'pt_library': pt_lib}))
                edges.append(("C" + str(idx) + "_A", "C" + str(idx + 1) + "_B"))
                edges.append(("C" + str(idx) + "_A", "C" + str(idx + 1) + "_A"))
                edges.append(("C" + str(idx) + "_B", "C" + str(idx + 1) + "_A"))
                edges.append(("C" + str(idx) + "_B", "C" + str(idx + 1) + "_B"))
            edges.append(("S0_A", "C0_A"))
            edges.append(("S0_B", "C0_B"))
            graph.add_nodes_from(nodes)
            graph.add_edges_from(edges)
            with RelTools(graph) as r:
                r.extract_reliability_formula(benchmark=benchmark)
                writer.writerow(benchmark.get_values() + [len])

if __name__ == "__main__":
    tmr_v111 = TmrV111Spec(
        [NonFuncParamas(random.uniform(0, 0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20))],
        NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20)))
    tmr_v123 = TmrV123Spec(
        [NonFuncParamas(random.uniform(0, 0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20))],
        [NonFuncParamas(random.uniform(0, 0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20))]
        )
    plain = PlainSpec(
        NonFuncParamas(random.uniform(0, 0.01), random.randrange(20), random.randrange(20), random.randrange(20)))


    v111_filename = "benchmarks/extraction-v111-rect.csv"
    v123_filename = "benchmarks/extraction-v123-rect.csv"
    plain_filename = "benchmarks/extraction-plain-rect.csv"
    v111_plain_filename = "benchmarks/extraction-v111-plain-rect.csv"
    v123_plain_filename = "benchmarks/extraction-v123-plain-rect.csv"
    v123_v111_filename = "benchmarks/extraction-v123-v111-rect.csv"
    v123_v111_plain_filename = "benchmarks/extraction-v123-v111-plain-rect.csv"
    if not os.path.isfile(v111_filename):
        test_rectangle(v111_filename, [tmr_v111])
    if not os.path.isfile(plain_filename):
        test_rectangle(plain_filename, [plain])
    if not os.path.isfile(v123_filename):
        test_rectangle(v123_filename, [tmr_v123])
    if not os.path.isfile(v111_plain_filename):
        test_rectangle(v111_plain_filename, [tmr_v111, plain])
    if not os.path.isfile(v123_plain_filename):
        test_rectangle(v123_plain_filename, [tmr_v123, plain])
    if not os.path.isfile((v123_v111_plain_filename)):
        test_rectangle(v123_v111_plain_filename, [tmr_v123, tmr_v111, plain])

    #111_df = pd.read_csv(v111_filename)
    v123_df = pd.read_csv(v123_filename)
    v111_df = pd.read_csv(v111_filename)
    plain_df = pd.read_csv(plain_filename)
    v111_plain_df = pd.read_csv(v111_plain_filename)
    v123_plain_df = pd.read_csv(v123_plain_filename)
    v123_v111_plain_df = pd.read_csv(v123_v111_plain_filename)
    res_df = []
    tmp_v123_df = v123_df[['len', 'total_ext_time']].copy()
    tmp_v123_df['pattern'] = "TMR-V123"
    res_df.append(tmp_v123_df)

    tmp_plain_df = plain_df[['len', 'total_ext_time']].copy()
    tmp_plain_df['pattern'] = "PLAIN"
    res_df.append(tmp_plain_df)

    tmp_v111_df = v111_df[['len', 'total_ext_time']].copy()
    tmp_v111_df['pattern'] = "TMR-V111"
    res_df.append(tmp_v111_df)

    tmp_v111_plain_df = v111_plain_df[['len', 'total_ext_time']].copy()
    tmp_v111_plain_df['pattern'] = "TMR-V111, PLAIN"
    res_df.append(tmp_v111_plain_df)

    tmp_v123_plain_df = v123_plain_df[['len', 'total_ext_time']].copy()
    tmp_v123_plain_df['pattern'] = "TMR-V123, PLAIN"
    res_df.append(tmp_v123_plain_df)

    tmp_v123_v111_plain_df = v123_v111_plain_df[['len', 'total_ext_time']].copy()
    tmp_v123_v111_plain_df['pattern'] = "TMR-V111, TMR-V123, PLAIN"
    res_df.append(tmp_v123_v111_plain_df)

    res = pd.concat(res_df, axis=0)
    fig = px.line(res, x="len",
                  y="total_ext_time",
                  color='pattern',
                  labels={"pattern": "Patterns", "total_ext_time": "Time (s)", "len": "Chain length"},
                  title="Multiple patterns comparison")
    fig.show()