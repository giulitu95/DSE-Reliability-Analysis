from patterns import TmrV111Spec, TmrV123Spec, PatternType
from params import NonFuncParamas
from rel_tools import RelTools
import networkx as nx
import csv
import time
import os
from typing import NamedTuple
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd


class Benchmark():
    def __init__(self):
        self.arch_creation_time = None
        self.bdd_qelim_time = None
        self.mincutsets_time= None
        self.sift = False
        self.sift_time= None
        self.rel_extraction_time = None
        self.total_ext_time = None

    @staticmethod
    def get_header():
        return ["arch_creation_time",
                "bdd_qelim_time",
                "mincutsets_time",
                "sift",
                "sift_time",
                "rel_extraction_time",
                "total_ext_time"]

    def get_values(self):
        return [self.arch_creation_time,
                self.bdd_qelim_time,
                self.mincutsets_time,
                self.sift,
                self.sift_time,
                self.rel_extraction_time,
                self.total_ext_time]


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


def test_chain_same_pt(file_name, pt_type, max_n_patt = 50, len_chain = 20):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(Benchmark.get_header() + ["n_pt"])  # header
        for n in range(1, max_n_patt):
            print("~" * 10 + " " + str(len) + " patterns " + "~" * 10)
            # Create pt_lib
            if pt_type == PatternType.TMR_V111:
                pt_lib = [TmrV111Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                        NonFuncParamas(0.1))] * n
            elif pt_type == PatternType.TMR_V123:
                pt_lib = [TmrV123Spec([NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                            [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)])] * n
            # Create graph
            graph = nx.DiGraph()
            graph.add_nodes_from([("S", {'type': 'SOURCE'})])
            graph.add_nodes_from([("C" + str(idx), {'type': 'COMP', 'pt_library': pt_lib}) for idx in range(len_chain)])
            graph.add_edges_from([("C" + str(idx), "C" + str(idx + 1)) for idx in range(len_chain - 1)] + [("S", "C0")])
            benchmark = Benchmark()
            r = RelTools(graph)
            r.extract_reliability_formula(benchmark=benchmark)
            writer.writerow(benchmark.get_values() + [n])


def plot_1pt_chain_benchmark(file, title):
    #df = pd.read_csv('benchmarks/tmr_V111_chain.csv')
    df = pd.read_csv(file)
    arch_df = df[['len', 'arch_creation_time']].copy()
    arch_df.columns = ['len', 'time']
    arch_df["section"] = 'arch_creation_time'
    qelim_df = df[['len', 'bdd_qelim_time']].copy()
    qelim_df.columns = ['len', 'time']
    qelim_df["section"] = "BDD qelim"
    min_df = df[['len', 'mincutsets_time']].copy()
    min_df.columns = ['len', 'time']
    min_df["section"] = "min cut-sets ext. time"
    sift_df = df[['len', 'sift_time']].copy()
    sift_df.columns = ['len', 'time']
    sift_df["section"] = 'sift_time'
    rel_df = df[['len', 'rel_extraction_time']].copy()
    rel_df.columns = ['len', 'time']
    rel_df["section"] = "Rel formula ext. time"
    res = pd.concat([qelim_df, min_df,  rel_df], axis=0)
    fig = px.area(res,
                  x="len",
                  y="time",
                  color="section",
                  labels={"section":"Section", "time": "Time (s)", "len": "Chain length"},
                  title=title)
    fig.show()


def plot_chain_same_pt(file, title):
    #df = pd.read_csv('benchmarks/chain_same_pt.csv')
    df = pd.read_csv(file)
    arch_df = df[["n_pt", 'arch_creation_time']].copy()
    arch_df.columns = ["n_pt", 'time']
    arch_df["section"] = 'arch_creation_time'
    qelim_df = df[["n_pt", 'bdd_qelim_time']].copy()
    qelim_df.columns = ["n_pt", 'time']
    qelim_df["section"] = "BDD qelim"
    min_df = df[["n_pt", 'mincutsets_time']].copy()
    min_df.columns = ["n_pt", 'time']
    min_df["section"] = "min cut-sets ext. time"
    sift_df = df[["n_pt", 'sift_time']].copy()
    sift_df.columns = ["n_pt", 'time']
    sift_df["section"] = 'sift_time'
    rel_df = df[["n_pt", 'rel_extraction_time']].copy()
    rel_df.columns = ["n_pt", 'time']
    rel_df["section"] = "Rel formula ext. time"
    res = pd.concat([qelim_df, min_df, rel_df], axis=0)
    fig = px.area(res,
                  x="n_pt",
                  y="time",
                  color="section",
                  labels={"section": "Section", "time": "Time (s)", "n_pt": "n. patterns"},
                  title=title)
    fig.show()

def plot_compare_pt(file_list):
    df_map = {pt_name: pd.read_csv(file) for file, pt_name in file_list.items()}
    res_df = []
    for name, df in df_map.items():
        tmp_df = df[['len', 'total_ext_time']].copy()
        tmp_df['pattern'] = name
        res_df.append(tmp_df)
    res = pd.concat(res_df, axis=0)
    fig = px.line(res, x="len", y="total_ext_time", color='pattern')
    fig.show()

lib_1pt = [TmrV111Spec([NonFuncParamas(0.1,1), NonFuncParamas(0.1,1), NonFuncParamas(0.02,1)],
                    NonFuncParamas(0.1,1)),
           TmrV123Spec([NonFuncParamas(0.1,1), NonFuncParamas(0.2,1), NonFuncParamas(0.02,1)],
                       [NonFuncParamas(0.1,1), NonFuncParamas(0.2,1), NonFuncParamas(0.02,1)])
           ]


#test_chain("benchmarks/V123_V111_chain.csv", lib_1pt)
#test_chain_same_pt("benchmarks/chain_same_pt_tmp.csv", PatternType.TMR_V123)
#plot_1pt_chain_benchmark("benchmarks/V123_V111_chain.csv", "TMR V111")
#plot_chain_same_pt()
#plot_compare_pt({"benchmarks/tmr_V111_chain.csv": "tmr-v111", "benchmarks/tmr_V123_chain.csv": "tmr-v123", "benchmarks/V123_V111_chain.csv": "tmr-v123, tmr-v111"})

