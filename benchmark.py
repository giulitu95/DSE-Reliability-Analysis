from patterns import TmrV111Spec, TmrV123Spec
from params import NonFuncParamas
from rel_tools import RelTools
import networkx as nx
import csv
import os
from typing import NamedTuple
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
sns.set_theme(style="whitegrid")


class Benchmark():
    def __init__(self):
        self.arch_creation_time = None
        self.bdd_qelim_time = None
        self.mincutsets_time= None
        self.sift = False
        self.sift_time= None
        self.rel_extraction_time = None

    @staticmethod
    def get_header():
        return ["arch_creation_time",
                "bdd_qelim_time",
                "mincutsets_time",
                "sift",
                "sift_time",
                "rel_extraction_time"]

    def get_values(self):
        return [self.arch_creation_time,
                self.bdd_qelim_time,
                self.mincutsets_time,
                self.sift,
                self.sift_time,
                self.rel_extraction_time]


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


def plot_chain_benchmark():
    df = pd.read_csv('benchmarks/chain2.csv')
    arch_df = df[['len', 'arch_creation_time']].copy()
    arch_df.columns = ['len', 'time']
    arch_df["section"] = 'arch_creation_time'
    qelim_df = df[['len', 'bdd_qelim_time']].copy()
    qelim_df.columns = ['len', 'time']
    qelim_df["section"] = 'bdd_qelim_time'
    min_df = df[['len', 'mincutsets_time']].copy()
    min_df.columns = ['len', 'time']
    min_df["section"] = 'mincutsets_time'
    sift_df = df[['len', 'sift_time']].copy()
    sift_df.columns = ['len', 'time']
    sift_df["section"] = 'sift_time'
    rel_df = df[['len', 'rel_extraction_time']].copy()
    rel_df.columns = ['len', 'time']
    rel_df["section"] = 'rel_extraction_time'
    res = pd.concat([qelim_df, min_df,  rel_df], axis=0)
    sns.lineplot(data=res, x ="len", y = "time", hue = "section", palette="tab10", linewidth=2.5)
    plt.show()
pt_lib1 = [
        TmrV111Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                    NonFuncParamas(0.1))
    ]
#test_chain("benchmarks/chain2.csv", pt_lib1)
plot_chain_benchmark()

