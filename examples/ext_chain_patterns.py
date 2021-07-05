import pandas as pd
from benchmark import Benchmark
from rel_tools import RelTools
import networkx as nx
import csv
import random
from params import NonFuncParamas
from patterns import *
import os
import plotly.express as px
#os.chdir("../")

def test_chain(file_name, pt_lib, max_len = 100):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(Benchmark.get_header() + ["len"]) # header
    for len in range(2, max_len):
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            benchmark = Benchmark()
            print("~"*10 + " " + str(len) + " len chain " + "~"*10)
            graph = nx.DiGraph()
            graph.add_nodes_from([("S", {'type': 'SOURCE'})])
            nodes = [("C" + str(idx), {'type': 'COMP', 'pt_library': pt_lib}) for idx in range(len)]
            graph.add_nodes_from(nodes)
            edges = [("C" + str(idx), "C" + str(idx + 1)) for idx in range(len - 1)]
            edges.append(("S", "C0"))
            graph.add_edges_from(edges)
            with RelTools(graph) as r:
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
    tmr_v001 = TmrV001Spec( [   NonFuncParamas(random.uniform(0,0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20))],
                            NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20)))
    tmr_v010 = TmrV010Spec( [   NonFuncParamas(random.uniform(0,0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20))],
                            NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20)))
    tmr_v012 = TmrV012Spec([    NonFuncParamas(random.uniform(0,0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20)),
                                NonFuncParamas(random.uniform(0,1), random.randrange(20),random.randrange(20), random.randrange(20))],
                           [    NonFuncParamas(random.uniform(0, 0.01), random.randrange(20), random.randrange(20),random.randrange(20)),
                                NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20)),]
                           )
    plain = PlainSpec(NonFuncParamas(random.uniform(0,0.01), random.randrange(20), random.randrange(20), random.randrange(20)))
    v111_filename = "benchmarks/extraction-v111-chain.csv"
    v123_filename = "benchmarks/extraction-v123-chain.csv"
    v012_filename = "benchmarks/extraction-v012-chain.csv"
    v111_v123_filename = "benchmarks/extraction-v111-v123-chain.csv"
    v111_v123_v012_filename = "benchmarks/extraction-v111-v123-v012-chain.csv"
    all_pt_filename = "benchmarks/extraction-allpt-chain.csv"
    plain_filename = "benchmarks/extraction-plain-chain.csv"
    v111_v123_v012_v001_filename = "benchmarks/extraction-v111_v123_v012_v001_chain.csv"
    v010_filename = "benchmarks/extraction-v010-chain.csv"

    if not os.path.isfile(v111_filename):
        test_chain(v111_filename, [tmr_v111])
    if not os.path.isfile(plain_filename):
        test_chain(plain_filename, [plain])
    if not os.path.isfile(v123_filename):
        test_chain(v123_filename, [tmr_v123])
    if not os.path.isfile(v111_v123_filename):
        test_chain(v111_v123_filename, [tmr_v111, tmr_v123])
    if not os.path.isfile(v111_v123_v012_filename):
        test_chain(v111_v123_v012_filename, [tmr_v111, tmr_v123, tmr_v012])
    if not os.path.isfile(v012_filename):
        test_chain(v012_filename, [tmr_v012])
    if not os.path.isfile(all_pt_filename):
        test_chain(all_pt_filename, [tmr_v111, tmr_v123, tmr_v001, tmr_v010, tmr_v012])
    if not os.path.isfile(v111_v123_v012_v001_filename):
        test_chain(v111_v123_v012_v001_filename, [tmr_v111, tmr_v123, tmr_v001, tmr_v012])
    if not os.path.isfile(v010_filename):
        test_chain(v010_filename, [tmr_v010])

    v111_df = pd.read_csv(v111_filename)
    v012_df = pd.read_csv(v012_filename)
    v123_df = pd.read_csv(v123_filename)
    plain_df = pd.read_csv(plain_filename)
    all_pt_df = pd.read_csv(all_pt_filename)
    v111_v123_df = pd.read_csv(v111_v123_filename)
    v111_v123_v012_df = pd.read_csv(v111_v123_v012_filename)
    v111_v123_v012_v001_df = pd.read_csv(v111_v123_v012_v001_filename)
    v010_df = pd.read_csv(v010_filename)

    res_df = []
    tmp_v111_df = v111_df[['len', 'total_ext_time']].copy()
    tmp_v111_df['pattern'] = "TMR-V111"
    res_df.append(tmp_v111_df)

    tmp_v010_df = v010_df[['len', 'total_ext_time']].copy()
    tmp_v010_df['pattern'] = "TMR-V010"
    res_df.append(tmp_v010_df)

    tmp_v123_df = v123_df[['len', 'total_ext_time']].copy()
    tmp_v123_df['pattern'] = "TMR-V123"
    res_df.append(tmp_v123_df)

    tmp_plain_df = plain_df[['len', 'total_ext_time']].copy()
    tmp_plain_df['pattern'] = "PLAIN"
    res_df.append(tmp_plain_df)

    tmp_v111_v123_df = v111_v123_df[['len', 'total_ext_time']].copy()
    tmp_v111_v123_df['pattern']= 'TMR-V111, TMR-V123'
    res_df.append(tmp_v111_v123_df)

    tmp_v111_v123_v012_df = v111_v123_v012_df[['len', 'total_ext_time']].copy()
    tmp_v111_v123_v012_df['pattern'] = 'TMR-V111, TMR-V123, TMR-V012'
    res_df.append(tmp_v111_v123_v012_df)

    tmp_v111_v123_v012_v001_df = v111_v123_v012_v001_df[['len', 'total_ext_time']].copy()
    tmp_v111_v123_v012_v001_df['pattern'] = 'TMR-V111, TMR-V123, TMR-V012, TMR-V001'
    res_df.append(tmp_v111_v123_v012_v001_df)

    tmp_all_pt_df = all_pt_df[['len', 'total_ext_time']].copy()
    tmp_all_pt_df['pattern'] = "ALL"
    res_df.append(tmp_all_pt_df)

    tmp_v012_df = v012_df[['len', 'total_ext_time']].copy()
    tmp_v012_df['pattern'] = 'TMR-V012'
    res_df.append(tmp_v012_df)

    res = pd.concat(res_df, axis=0)

    fig = px.line(res, x="len",
                  y="total_ext_time",
                  color='pattern',
                  labels={"pattern": "Patterns", "total_ext_time": "Time (s)", "len": "Chain length"},
                  title="Multiple patterns comparison")
    fig.show()