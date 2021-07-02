import fractions
from pysmt.shortcuts import Optimizer
from rel_tools import RelTools
from pysmt.optimization.goal import MinimizationGoal
import time
import resource
from approach import Hybrid, Enumerative, Symbolic

class Dse:
    def __init__(self, graph):
        self._graph = graph

    def optimize(self, benchmark=None, approch="symbolic"):
            if approch == "symbolic":
                appr = Symbolic(self._graph)
                cost, cost_formula = appr.extract_cost()
                power, power_formula = appr.extract_power()
                size, size_formula = appr.extract_size()
                rel, rel_formula = appr.extract_rel()
            elif approch == "hybrid":
                appr = Hybrid(self._graph, cfg_encoding="BOOL")
                cost, cost_formula = appr.extract_cost()
                power, power_formula = appr.extract_power()
                size, size_formula = appr.extract_size()
                rel, rel_formula = appr.extract_rel()

                #rel, rel_formula = h.extract_rel(cfg_type="INT")
            else:
                appr = Enumerative(self._graph)
                cost, cost_formula = appr.extract_cost()
                power, power_formula = appr.extract_power()
                size, size_formula = appr.extract_size()
                rel, rel_formula = appr.extract_rel()

            #objective functions
            rel_obj = MinimizationGoal(rel)
            cost_obj = MinimizationGoal(cost)
            power_obj = MinimizationGoal(power)
            size_obj = MinimizationGoal(size)

            #print(rel_formula.serialize())
            #print(cost_formula.serialize())
            #print(power_formula.serialize())
            #print(size_formula.serialize())

            with Optimizer(name="z3") as opt:
                opt.add_assertion(rel_formula)
                opt.add_assertion(cost_formula)
                opt.add_assertion(power_formula)
                opt.add_assertion(size_formula)
                #Start timer
                opt.add_assertion(appr.r.compatibility_constr)
                time_start = time.perf_counter()
                res = opt.pareto_optimize([cost_obj, power_obj, size_obj, rel_obj])
                print("[Optimizer] Find Pareto points...")
                pareto_points = []
                counter = 0
                for model, r in res:
                    counter = counter + 1
                    print("Solution " + str(counter))
                    #print("   Patterns:")
                    #print("   " + str(appr.get_patterns(model)))
                    print("   Parameters:")
                    print("   Cost: " + str(r[0]) + ", Power " + str(r[1]) + ", Size: " + str(r[2]) + ", F-prob: ", str(float(fractions.Fraction(r[3].serialize()))))
                    pareto_points.append((model, r))
                print("[Optimizer] Done!")
            appr.close()
            if benchmark is not None: benchmark.optimization_time = time.perf_counter() - time_start
            return pareto_points