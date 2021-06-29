from params import NonFuncParamas
from patterns import TmrV123Spec
import pandas as pd
import random
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
    tmr_v123 = TmrV123Spec(
        [NonFuncParamas(random.uniform(0, 0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20))],
        [NonFuncParamas(random.uniform(0, 0.01), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20)),
         NonFuncParamas(random.uniform(0, 1), random.randrange(20), random.randrange(20), random.randrange(20))]
        )
    v123_filename = "benchmarks/extraction-v123-chain.csv"
    if not os.path.isfile(v123_filename):
        test_chain(v123_filename, [tmr_v123])

    v123_df = pd.read_csv(v123_filename)
    arch_df = v123_df[['len', 'arch_creation_time']].copy()
    arch_df.columns = ['len', 'time']
    arch_df["section"] = 'arch_creation_time'
    qelim_df = v123_df[['len', 'bdd_qelim_time']].copy()
    qelim_df.columns = ['len', 'time']
    qelim_df["section"] = "BDD qelim"
    sift_df = v123_df[['len', 'sift_time']].copy()
    sift_df.columns = ['len', 'time']
    sift_df["section"] = 'sift_time'
    rel_df = v123_df[['len', 'rel_extraction_time']].copy()
    rel_df.columns = ['len', 'time']
    rel_df["section"] = "Rel formula ext. time"
    res = pd.concat([qelim_df, rel_df], axis=0)
    fig = px.area(res,
                  x="len",
                  y="time",
                  color="section",
                  labels={"section":"Section", "time": "Time (s)", "len": "Chain length"},
                  title="TMR-V123 chain: reliability extraction")
    fig.show()