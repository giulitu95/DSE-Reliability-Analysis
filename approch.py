import itertools
from patterns import *
import copy
from rel_tools import RelTools
from tqdm import tqdm

class Enumerative:
    # TODO: it works only with compatible patterns!
    def __init__(self, graph):
        self._graph = graph
        self._n_cfg = 1
        self._ptlibs = []
        # Prepare list of libraries: [[lib1], [lib2], ...]
        for node in self._graph.nodes:
            if self._graph.nodes[node]["type"] == "COMP":
                lib = self._graph.nodes[node]["pt_library"]
                self._n_cfg = self._n_cfg * len(lib)  # Number of elements in the cartesiona product
                self._ptlibs.append(lib)
        #self._cfg_bv = Symbol("cfg", BVType(math.ceil(math.log(n_cfg, 2))))
        self._cfg_id = Symbol("cfg", INT)
        self._rel = Symbol("R", REAL)
        self._cost = Symbol("COST", REAL)

    def extract_cost(self):
        enum_cost = []
        for idx, combination in enumerate(itertools.product(*self._ptlibs)):
            comb = [*combination][0]
            cost = 0
            for params in comb.param_list:
                cost = cost + params.cost
            enum_cost.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._cost, Real(cost))))
        return self._cost, And(And(enum_cost), LT(self._cfg_id, Int(self._n_cfg)))

    def extract_power(self):
        enum_power = []
        for idx, combination in enumerate(itertools.product(*self._ptlibs)):
            comb = [*combination][0]
            cost = 0
            for params in comb.param_list:
                power = power + params.power
            enum_power.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._power, Real(power))))
        return self._power, And(And(enum_power), LT(self._cfg_id, Int(self._n_cfg)))

    def extract_rel(self):
        # Perform the cartesian product to find all combinations and create the graph
        enum_rel = []
        for idx, combination in enumerate(itertools.product(*self._ptlibs)):
            print("[Enumerative] ~~~ " + str(idx+1) + "th combination out of " + str(self._n_cfg) + " ~~~")
            comb = [*combination]
            # make a copy of the graph changing the patterns library for each component
            ng = copy.deepcopy(self._graph)
            for node in ng.nodes:
                if ng.nodes[node]["type"]  == "COMP":
                    ng.nodes[node]["pt_library"] = [comb.pop(0)]
            r = RelTools(ng)
            rel_symbol, formula = r.extract_reliability_formula()
            # Find reliability value for this combination
            with Solver(name="z3") as solver:
                solver.add_assertion(formula)
                solver.add_assertion(r.prob_constr)
                solver.solve()
                rel = solver.get_value(rel_symbol)
            enum_rel.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._rel, rel)))
        return self._rel, And(And(enum_rel), LT(self._cfg_id, Int(self._n_cfg)))


class Hybrid:
    def __init__(self, graph, cfg_encoding="BOOL"):
        self._graph = graph
        self._rel = Symbol("R", REAL)
        self._cost = Symbol("COST", REAL)
        self._power = Symbol("POWER", REAL)
        self._n_cfg = 1
        self.r = RelTools(self._graph)
        self._cfg_encoding = cfg_encoding
        # Prepare list of libraries: [[lib1], [lib2], ...]
        for node in self._graph.nodes:
            if self._graph.nodes[node]["type"] == "COMP":
                lib = self._graph.nodes[node]["pt_library"]
                self._n_cfg = self._n_cfg * len(lib)  # Number of elements in the cartesian product
                print(self._n_cfg)
        self._cfg_id = Symbol("cfg", INT)

    def __gen_cfg(self, node2conf2pt):
        cfgs_node= []
        for node, conf2pt in node2conf2pt.items():
            cfgs_node.append(list(conf2pt.keys()))
        for idx, combination in enumerate(itertools.product(*cfgs_node)):
            yield Equals(self._cfg_id, Int(idx)), And([*combination])

    def extract_cost(self):
        enum_cost = []
        cfgs_node = []
        all_cfg2pt = {}
        for node, conf2pt in self.r.conf2pt.items():
            cfgs_node.append(list(conf2pt.keys()))
            for cfg, pt in conf2pt.items():
                all_cfg2pt[cfg] = pt
        pbar = tqdm(total=self._n_cfg, desc="Finding Costs")
        for idx, combination in enumerate(itertools.product(*cfgs_node)):
            pbar.update(1)
            comb = [*combination]
            cost = 0
            for cfg in comb:
                for params in all_cfg2pt[cfg].param_list:
                    cost = cost + params.cost
            if self._cfg_encoding == "INT":
                enum_cost.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._cost, Real(cost))))
            else:
                enum_cost.append(Implies(And(comb), Equals(self._cost, Real(cost))))
        pbar.close()
        return self._cost, And(And(enum_cost), self.r.conf_formula)

    def extract_power(self):
        enum_power = []
        cfgs_node = []
        all_cfg2pt = {}
        for node, conf2pt in self.r.conf2pt.items():
            cfgs_node.append(list(conf2pt.keys()))
            for cfg, pt in conf2pt.items():
                all_cfg2pt[cfg] = pt
        pbar = tqdm(total=self._n_cfg, desc="Finding Power consumptions")
        for idx, combination in enumerate(itertools.product(*cfgs_node)):
            pbar.update(1)
            comb = [*combination]
            power = 0
            for cfg in comb:
                for params in all_cfg2pt[cfg].param_list:
                    power = power + params.power
            if self._cfg_encoding == "INT":
                enum_power.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._power, Real(power))))
            else:
                enum_power.append(Implies(And(comb), Equals(self._power, Real(power))))
        pbar.close()
        return self._power, And(And(enum_power), self.r.conf_formula)

    def extract_rel(self):
        rel_symbol, formula = self.r.extract_reliability_formula()
        enum_rel = []
        cfgs_node = []
        for node, conf2pt in self.r.conf2pt.items():
            cfgs_node.append(list(conf2pt.keys()))

        with Solver(name="z3") as solver:
            pbar = tqdm(total=self._n_cfg, desc="Finding Reliabilities")
            for idx, combination in enumerate(itertools.product(*cfgs_node)):
                pbar.update(1)
                bool_cfg = And([*combination])
                int_cfg = Equals(self._cfg_id, Int(idx))
                solver.add_assertion(formula)
                solver.add_assertion(bool_cfg)
                solver.add_assertion(self.r.prob_constr)
                solver.solve()
                rel = solver.get_value(rel_symbol)
                if self._cfg_encoding == "INT": enum_rel.append(Implies(int_cfg, Equals(self._rel, rel)))
                else: enum_rel.append(Implies(bool_cfg, Equals(self._rel, rel)))
                solver.reset_assertions()
            pbar.close()
        if self._cfg_encoding == "BOOL": res = self._rel, And(And(enum_rel), self.r.conf_formula)
        else: res = self._rel, And(And(enum_rel), LT(self._cfg_id, Int(self._n_cfg)))
        return res


class Symbolic:
    def __init__(self, graph):
        self._graph = graph
        self._r = RelTools(self._graph)

    def extract_cost(self):
        cost_constr = []
        node_costs = []
        for nx_node, an in self._r.nxnode2archnode.items():
            node_cost = Symbol(nx_node + "_COST", REAL)
            node_costs.append(node_cost)
            for cfg, pt in an.conf2pt.items():
                pt_cost = 0
                for params in pt.param_list:
                    pt_cost = pt_cost + params.cost
                cost_constr.append(Implies(cfg, Equals(node_cost, Real(pt_cost))))
        cost_assignments = And(cost_constr)
        cost = Symbol("cost", REAL)
        return cost, And([Equals(cost, Plus(node_costs)), cost_assignments, self._r.conf_formula])

    def extract_power(self):
        power_constr = []
        node_powers = []
        for nx_node, an in self._r.nxnode2archnode.items():
            node_power = Symbol(nx_node + "_POWER", REAL)
            node_powers.append(node_power)
            for cfg, pt in an.conf2pt.items():
                pt_power = 0
                for params in pt.param_list:
                    pt_power = pt_power + params.power
                power_constr.append(Implies(cfg, Equals(node_power, Real(pt_power))))
        power_assignments = And(power_constr)
        power = Symbol("power", REAL)
        return power, And([Equals(power, Plus(node_powers)), power_assignments, self._r.conf_formula])

    def extract_rel(self):
        rel, formula = self._r.extract_reliability_formula()
        return rel, And([formula, self._r.conf_formula, self._r.prob_constr])


'''random.seed(a=1, version=2)
pt_lib1 = [TmrV111Spec([NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20))],
                       NonFuncParamas(random.uniform(0,1), random.randrange(20))),
           TmrV111Spec([NonFuncParamas(random.uniform(0, 1),random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1),random.randrange(20))],
                       NonFuncParamas(random.uniform(0, 1),random.randrange(20))),
           TmrV111Spec([NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20))],
                       NonFuncParamas(random.uniform(0, 1), random.randrange(20)))
           ]
pt_lib2 = [TmrV111Spec([NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0,1), random.randrange(20))],
                       NonFuncParamas(random.uniform(0,1), random.randrange(20))),
           TmrV111Spec([NonFuncParamas(random.uniform(0, 1),random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1), random.randrange(20)),
                        NonFuncParamas(random.uniform(0, 1),random.randrange(20))],
                       NonFuncParamas(random.uniform(0, 1),random.randrange(20)))]

g = nx.DiGraph()
g.add_nodes_from([  ("S1", {'type': 'SOURCE'}),
                    ("C1", {'type': 'COMP', 'pt_library': pt_lib1}),
                    ("C2", {'type': 'COMP', 'pt_library': pt_lib1}),
                    ("C3", {'type': 'COMP', 'pt_library': pt_lib1}),
])
g.add_edge('S1', 'C1')
g.add_edge('C1', 'C2')
g.add_edge('C2', 'C3')


h = Hybrid(g)
h.extract_cost()
a, b = h.extract_rel(cfg_type="BOOL")
print(b.serialize())'''

# (((('CONF_C1[0]' ? ('rel_\'CONF_C1[0]\'-0' = rel_C1_F0-19) : ('rel_\'CONF_C1[0]\'-0' = rel_C1_F0-1)) &
# (rel_C1_F0-1 = ((p0_C1 * rel_C1_F1-18) + ((1.0 - p0_C1) * rel_C1_F1-2))) &
# (rel_C1_F1-2 = ((p1_C1 * rel_C1_F2-17) + ((1.0 - p1_C1) * rel_C1_F3-3))) &
# (rel_C1_F3-3 = ((p3_C1 * rel_TRUE--1) + ((1.0 - p3_C1) * 'rel_\'CONF_C2[0]\'-4'))) &
# ('CONF_C2[0]' ? ('rel_\'CONF_C2[0]\'-4' = rel_C2_F0-10) : ('rel_\'CONF_C2[0]\'-4' = rel_C2_F0-5)) &
# (rel_C2_F0-5 = ((p0_C2 * rel_C2_F1-9) + ((1.0 - p0_C2) * rel_C2_F1-6))) &
# (rel_C2_F1-6 = ((p1_C2 * rel_C2_F2-8) + ((1.0 - p1_C2) * rel_C2_F3-7))) &
# (rel_C2_F3-7 = ((p3_C2 * rel_TRUE--1) + ((1.0 - p3_C2) * rel_FALSE--2))) &
# (rel_FALSE--2 = 0.0) &
# (rel_TRUE--1 = 1.0) &
# (rel_C2_F2-8 = ((p2_C2 * rel_TRUE--1) + ((1.0 - p2_C2) * rel_C2_F3-7))) &
# (rel_C2_F1-9 = ((p1_C2 * rel_TRUE--1) + ((1.0 - p1_C2) * rel_C2_F2-8))) &
# (rel_C2_F0-10 = ((p0_C2 * rel_C2_F1-16) + ((1.0 - p0_C2) * rel_C2_F1-11))) &
# (rel_C2_F1-11 = ((p1_C2 * rel_C2_F2-15) + ((1.0 - p1_C2) * rel_C2_F3-12))) &
# (rel_C2_F3-12 = ((p3_C2 * rel_TRUE--1) + ((1.0 - p3_C2) * rel_C2_F4-13))) &
# (rel_C2_F4-13 = ((p4_C2 * rel_TRUE--1) + ((1.0 - p4_C2) * rel_C2_F5-14))) &
# (rel_C2_F5-14 = ((p5_C2 * rel_TRUE--1) + ((1.0 - p5_C2) * rel_FALSE--2))) &
# (rel_C2_F2-15 = ((p2_C2 * rel_TRUE--1) + ((1.0 - p2_C2) * rel_C2_F3-12))) &
# (rel_C2_F1-16 = ((p1_C2 * rel_TRUE--1) + ((1.0 - p1_C2) * rel_C2_F2-15))) &
# (rel_C1_F2-17 = ((p2_C1 * rel_TRUE--1) + ((1.0 - p2_C1) * rel_C1_F3-3))) &
# (rel_C1_F1-18 = ((p1_C1 * rel_TRUE--1) + ((1.0 - p1_C1) * rel_C1_F2-17))) &
# (rel_C1_F0-19 = ((p0_C1 * rel_C1_F1-37) + ((1.0 - p0_C1) * rel_C1_F1-20))) &
# (rel_C1_F1-20 = ((p1_C1 * rel_C1_F2-36) + ((1.0 - p1_C1) * rel_C1_F3-21))) &
# (rel_C1_F3-21 = ((p3_C1 * rel_C1_F4-33) + ((1.0 - p3_C1) * rel_C1_F4-22))) &
# (rel_C1_F4-22 = ((p4_C1 * rel_C1_F5-29) + ((1.0 - p4_C1) * rel_C1_F5-23))) &
# (rel_C1_F5-23 = ((p5_C1 * 'rel_\'CONF_C2[0]\'-24') + ((1.0 - p5_C1) * 'rel_\'CONF_C2[0]\'-4'))) &
# ('CONF_C2[0]' ? ('rel_\'CONF_C2[0]\'-24' = rel_C2_F0-27) : ('rel_\'CONF_C2[0]\'-24' = rel_C2_F0-25)) &
# (rel_C2_F0-25 = ((p0_C2 * rel_TRUE--1) + ((1.0 - p0_C2) * rel_C2_F1-26))) &
# (rel_C2_F1-26 = ((p1_C2 * rel_TRUE--1) + ((1.0 - p1_C2) * rel_C2_F3-7))) &
# (rel_C2_F0-27 = ((p0_C2 * rel_TRUE--1) + ((1.0 - p0_C2) * rel_C2_F1-28))) &
# (rel_C2_F1-28 = ((p1_C2 * rel_TRUE--1) + ((1.0 - p1_C2) * rel_C2_F3-12))) &
# (rel_C1_F5-29 = ((p5_C1 * rel_TRUE--1) + ((1.0 - p5_C1) * 'rel_\'CONF_C2[0]\'-30'))) &
# ('CONF_C2[0]' ? ('rel_\'CONF_C2[0]\'-30' = rel_C2_F0-32) : ('rel_\'CONF_C2[0]\'-30' = rel_C2_F0-31)) &
# (rel_C2_F0-31 = ((p0_C2 * rel_TRUE--1) + ((1.0 - p0_C2) * rel_C2_F2-8))) &
# (rel_C2_F0-32 = ((p0_C2 * rel_TRUE--1) + ((1.0 - p0_C2) * rel_C2_F2-15))) &
# (rel_C1_F4-33 = ((p4_C1 * rel_TRUE--1) + ((1.0 - p4_C1) * rel_C1_F5-34))) &
# (rel_C1_F5-34 = ((p5_C1 * rel_TRUE--1) + ((1.0 - p5_C1) * 'rel_\'CONF_C2[0]\'-35'))) &
# ('CONF_C2[0]' ? ('rel_\'CONF_C2[0]\'-35' = rel_C2_F1-16) : ('rel_\'CONF_C2[0]\'-35' = rel_C2_F1-9)) &
# (rel_C1_F2-36 = ((p2_C1 * rel_TRUE--1) + ((1.0 - p2_C1) * rel_C1_F3-21))) &
# (rel_C1_F1-37 = ((p1_C1 * rel_TRUE--1) + ((1.0 - p1_C1) * rel_C1_F2-36)))) &
# (Rel = 'rel_\'CONF_C1[0]\'-0')) & ((! False) & (! False)) &
#
# ((((! 'CONF_C2[0]') -> (p0_C2 = 1080863910568919/36028797018963968)) & ((! 'CONF_C2[0]') -> (p1_C2 = 1080863910568919/36028797018963968)) & ((! 'CONF_C2[0]') -> (p2_C2 = 1080863910568919/36028797018963968)) & ((! 'CONF_C2[0]') -> (p3_C2 = 5764607523034235/576460752303423488)) & ('CONF_C2[0]' -> (p0_C2 = 1080863910568919/36028797018963968)) & ('CONF_C2[0]' -> (p1_C2 = 1080863910568919/36028797018963968)) & ('CONF_C2[0]' -> (p2_C2 = 1080863910568919/36028797018963968)) & ('CONF_C2[0]' -> (p3_C2 = 5764607523034235/576460752303423488)) & ('CONF_C2[0]' -> (p4_C2 = 5764607523034235/576460752303423488)) & ('CONF_C2[0]' -> (p5_C2 = 5764607523034235/576460752303423488))) & (((! 'CONF_C1[0]') -> (p0_C1 = 1080863910568919/36028797018963968)) & ((! 'CONF_C1[0]') -> (p1_C1 = 1080863910568919/36028797018963968)) & ((! 'CONF_C1[0]') -> (p2_C1 = 1080863910568919/36028797018963968)) & ((! 'CONF_C1[0]') -> (p3_C1 = 5764607523034235/576460752303423488)) & ('CONF_C1[0]' -> (p0_C1 = 1080863910568919/36028797018963968)) & ('CONF_C1[0]' -> (p1_C1 = 1080863910568919/36028797018963968)) & ('CONF_C1[0]' -> (p2_C1 = 1080863910568919/36028797018963968)) & ('CONF_C1[0]' -> (p3_C1 = 5764607523034235/576460752303423488)) & ('CONF_C1[0]' -> (p4_C1 = 5764607523034235/576460752303423488)) & ('CONF_C1[0]' -> (p5_C1 = 5764607523034235/576460752303423488)))))