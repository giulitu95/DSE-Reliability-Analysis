from params import NonFuncParamas
from patterns import TmrV111Spec
import csv
import pandas as pd
import random
import os
import plotly.express as px
import networkx as nx
from benchmark import Benchmark
from rel_tools import RelTools
os.chdir("../")

def test_rectangle(file_name, pt_lib, max_len = 100):
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
                edges.append(("C" + str(idx) + "_B", "C" + str(idx + 1) + "_A"))
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
    v111_filename = "benchmarks/extraction-v111-rect.csv"
    if not os.path.isfile(v111_filename):
        test_rectangle(v111_filename, [tmr_v111])

    v111_df = pd.read_csv(v111_filename)
    arch_df = v111_df[['len', 'arch_creation_time']].copy()
    arch_df.columns = ['len', 'time']
    arch_df["section"] = 'arch_creation_time'
    qelim_df = v111_df[['len', 'bdd_qelim_time']].copy()
    qelim_df.columns = ['len', 'time']
    qelim_df["section"] = "BDD qelim"
    sift_df = v111_df[['len', 'sift_time']].copy()
    sift_df.columns = ['len', 'time']
    sift_df["section"] = 'sift_time'
    rel_df = v111_df[['len', 'rel_extraction_time']].copy()
    rel_df.columns = ['len', 'time']
    rel_df["section"] = "Rel formula ext. time"
    res = pd.concat([qelim_df, rel_df], axis=0)
    fig = px.area(res,
                  x="len",
                  y="time",
                  color="section",
                  labels={"section":"Section", "time": "Time (s)", "len": "Chain length"},
                  title="TMR-V111 rectangular: reliability extraction")
    fig.show()