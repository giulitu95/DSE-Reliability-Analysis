import itertools
from patterns import *
import copy
from rel_tools import RelTools
from tqdm import tqdm
import time

class Approch:
    def __init__(self, graph):
        self._graph = graph
        self._r = RelTools(graph)
    def get_patterns(self, model):
        res = {}
        for node, conf2pt in self._r.node2conf2pt.items():
            for conf, pt in conf2pt.items():
                if model.get_py_value(conf, model_completion=True):
                    res[node] = pt
        return res

    @property
    def r(self):
        return self._r

    @abc.abstractmethod
    def close(self):
        pass


# Approach 1: Enumerative
class Enumerative(Approch):
    # TODO: it works only with compatible patterns!
    def __init__(self, graph):
        super().__init__(graph)
        self._n_cfg = 1
        self._ptlibs = []
        # Prepare list of libraries: [[lib1], [lib2], ...]
        for node in self._graph.nodes:
            if self._graph.nodes[node]["type"] == "COMP":
                lib = self._graph.nodes[node]["pt_library"]
                self._n_cfg = self._n_cfg * len(lib)  # Number of elements in the cartesian product
                self._ptlibs.append(lib)
        #self._cfg_bv = Symbol("cfg", BVType(math.ceil(math.log(n_cfg, 2))))
        self._cfg_id = Symbol("cfg", INT)
        self._rel = Symbol("R", REAL)
        self._cost = Symbol("COST", REAL)
        self._power = Symbol("POWER", REAL)
        self._size = Symbol("SIZE", REAL)

    #Cost function: Cost
    def extract_cost(self):
        enum_cost = []
        for idx, combination in enumerate(itertools.product(*self._ptlibs)):
            comb = [*combination][0]
            cost = 0
            for params in comb.param_list:
                cost = cost + params.cost
            enum_cost.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._cost, Real(cost))))
        return self._cost, And(And(enum_cost), LT(self._cfg_id, Int(self._n_cfg)))


    # Cost function: Power Consumption
    def extract_power(self):
        enum_power = []
        for idx, combination in enumerate(itertools.product(*self._ptlibs)):
            comb = [*combination][0]
            power = 0
            for params in comb.param_list:
                power = power + params.power
            enum_power.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._power, Real(power))))
        return self._power, And(And(enum_power), LT(self._cfg_id, Int(self._n_cfg)))

    # Cost function: Size area
    def extract_size(self):
        enum_size = []
        for idx, combination in enumerate(itertools.product(*self._ptlibs)):
            comb = [*combination][0]
            size = 0
            for params in comb.param_list:
                size = size + params.size
            enum_size.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._size, Real(size))))
        return self._size, And(And(enum_size), LT(self._cfg_id, Int(self._n_cfg)))

    # Cost function: Execution Time
    # TBD?


    def extract_rel(self, benchmark=False):
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
            with RelTools(ng) as r:
                rel_symbol, formula = r.extract_reliability_formula()
            # Find reliability value for this combination
            with Solver(name="z3") as solver:
                solver.add_assertion(formula)
                solver.add_assertion(r.prob_constr)
                solver.solve()
                rel = solver.get_value(rel_symbol)
            enum_rel.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._rel, rel)))
        return self._rel, And(And(enum_rel), LT(self._cfg_id, Int(self._n_cfg)))

# Approach 2: Hybrid
class Hybrid(Approch):
    def __init__(self, graph, cfg_encoding="BOOL"):
        super().__init__(graph)
        self._rel = Symbol("R", REAL)
        self._cost = Symbol("COST", REAL)
        self._power = Symbol("POWER", REAL)
        self._size = Symbol("SIZE", REAL)
        self._n_cfg = 1
        self._cfg_encoding = cfg_encoding
        # Prepare list of libraries: [[lib1], [lib2], ...]
        for node in self._graph.nodes:
            if self._graph.nodes[node]["type"] == "COMP":
                lib = self._graph.nodes[node]["pt_library"]
                self._n_cfg = self._n_cfg * len(lib)  # Number of elements in the cartesiona product
        self._cfg_id = Symbol("cfg", INT)

    def close(self):
        self._r.close()

    # Cost function: Cost
    def extract_cost(self):
        enum_cost = []
        cfgs_node = []
        all_cfg2pt = {}
        for node, conf2pt in self._r.node2conf2pt.items():
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
        return self._cost, And(And(enum_cost), self._r.conf_formula)

    # Cost function: Power Consumption
    def extract_power(self):
        enum_power = []
        cfgs_node = []
        all_cfg2pt = {}
        for node, conf2pt in self._r.node2conf2pt.items():
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
        return self._power, And(And(enum_power), self._r.conf_formula)

    # Cost function: Size Area
    def extract_size(self):
        enum_size = []
        cfgs_node = []
        all_cfg2pt = {}
        for node, conf2pt in self._r.node2conf2pt.items():
            cfgs_node.append(list(conf2pt.keys()))
            for cfg, pt in conf2pt.items():
                all_cfg2pt[cfg] = pt
        pbar = tqdm(total=self._n_cfg, desc="Finding Size areas")
        for idx, combination in enumerate(itertools.product(*cfgs_node)):
            pbar.update(1)
            comb = [*combination]
            size = 0
            for cfg in comb:
                for params in all_cfg2pt[cfg].param_list:
                    size = size + params.size
            if self._cfg_encoding == "INT":
                enum_size.append(Implies(Equals(self._cfg_id, Int(idx)), Equals(self._size, Real(size))))
            else:
                enum_size.append(Implies(And(comb), Equals(self._size, Real(size))))
        pbar.close()
        return self._size, And(And(enum_size), self._r.conf_formula)

    def extract_rel(self, benchmark=None):
        rel_symbol, formula = self._r.extract_reliability_formula(benchmark=benchmark)
        enum_rel = []
        cfgs_node = []
        # Map each node to all its possible configurations
        # Notice: Impossible configurations are not included!
        for node, conf2pt in self._r.node2conf2pt.items():
            cfgs_node.append(list(conf2pt.keys()))
        start_time = time.perf_counter()
        with Solver(name="z3") as solver:
            pbar = tqdm(total=self._n_cfg, desc="Finding Reliabilities")
            # Iterate over the all possible configurations
            for idx, combination in enumerate(itertools.product(*cfgs_node)):
                pbar.update(1)
                bool_cfg = And([*combination])
                int_cfg = Equals(self._cfg_id, Int(idx))
                solver.add_assertion(formula)
                solver.add_assertion(bool_cfg)
                solver.add_assertion(self._r.prob_constr)
                solver.solve()
                rel = solver.get_value(rel_symbol)
                if self._cfg_encoding == "INT": enum_rel.append(Implies(int_cfg, Equals(self._rel, rel)))
                else: enum_rel.append(Implies(bool_cfg, Equals(self._rel, rel)))
                solver.reset_assertions()
            pbar.close()
        if benchmark is not None: benchmark.rel_enum_time = time.perf_counter() - start_time
        if self._cfg_encoding == "BOOL": res = self._rel, And(enum_rel)
        else: res = self._rel, And(And(enum_rel), LT(self._cfg_id, Int(self._n_cfg)))
        return res

# Approach 3: Symbolic
class Symbolic(Approch):
    def __init__(self, graph):
        super().__init__(graph)

    def close(self):
        self._r.close()

    # Cost function: Cost
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

    # Cost function: Power Consumption
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

    # Cost function: Size Area
    def extract_size(self):
        size_constr = []
        node_sizes = []
        for nx_node, an in self._r.nxnode2archnode.items():
            node_size = Symbol(nx_node + "_SIZE", REAL)
            node_sizes.append(node_size)
            for cfg, pt in an.conf2pt.items():
                pt_size = 0
                for params in pt.param_list:
                    pt_size = pt_size + params.size
                size_constr.append(Implies(cfg, Equals(node_size, Real(pt_size))))
        size_assignments = And(size_constr)
        size = Symbol("size", REAL)
        return size, And([Equals(size, Plus(node_sizes)), size_assignments, self._r.conf_formula])

    # Cost function: Reliability
    def extract_rel(self, benchmark=None):
        rel, formula = self._r.extract_reliability_formula(benchmark=benchmark)
        return rel, And([formula, self._r.conf_formula, self._r.prob_constr])


