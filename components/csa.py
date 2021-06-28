#!/usr/bin/env python

from patterns import PatternType, PatternDefinition
from components.component import ComponentType, Component
from components.stage import Stage
from pysmt.shortcuts import *
import os
from pysmt.parsing import parse
from allsmt import allsmt

__author__ = "Giuliano Turri"


class Csa(Component):
    '''
    Class providing methods and attribute to compute the formula which represents the sequential composition of
    components Concretizer - Stage - Abstractor
    '''

    def __init__(self, pt_definition: PatternDefinition):
        """
        Create a Csa
        :param pt_definition: definition of a pattern
        """
        print("[" + pt_definition.comp_name + "-" + pt_definition.pt_type.name + "]" + " Initialize CSA")
        self._pt_definition = pt_definition
        self._stage = Stage(pt_definition)
        self._comp_n_inputs = pt_definition.comp_n_inputs
        # We can also delete this, this is needed only in order to compyte the behaviour formula which actually we don't need
        self._concretizer = Concretizer("[" + pt_definition.comp_name + "-" + pt_definition.pt_type.name + "].concr",
                                        pt_definition.comp_n_inputs, self._stage
                                        )
        self._abstractor = Abstractor("[" + pt_definition.comp_name + "-" + pt_definition.pt_type.name + "].abstr",
                                      self._stage
                                      )

        super(Csa, self).__init__("[" + pt_definition.comp_name + "-" + pt_definition.pt_type.name + "].csa",
                                  ComponentType.CSA, self._concretizer.input_ports,
                                  self._abstractor.output_ports,
                                  fault_atoms=self._stage.fault_atoms
                                  )
        self._behaviour_formula = And(
            [self._stage.behaviour_formula, self._concretizer.behaviour_formula, self._abstractor.behaviour_formula])
        # Ports which have not yet been connected
        self._available_ports = self._concretizer.indexed_in_ports.copy()

    def get_update_available_ports(self):
        """
        Method needed when multiple csa have to be connected together. It retrieves the ports of the modules
        which have not yet been connected. Once the method is called, the retrieved ports are tagged as "connected"
        and they are not retrieved the next time the method is called.
        :return: the next unconnected ports
        """
        assert self._available_ports, "[CSA] no more available port for connection"
        ports = self._available_ports[0]
        self._available_ports.remove(ports)
        return ports

    def reset_available_ports(self):
        self._available_ports = self._concretizer.indexed_in_ports.copy()

    def get_qe_formula(self):
        """
        Create a behaviour formula of the Csa containing only boolean atoms (faulty atoms, concretizer input ports and abstractor output ports)
        :return: behaviour boolean formula
        """
        #print("[" + self._pt_definition.comp_name + "-" + self._pt_definition.pt_type.name + "]" + " Get AllSMT behaviour formula: ")
        file_name = os.path.join('csa-cache/', self._pt_definition.pt_type.name + "_" + str(self._pt_definition.comp_n_inputs) + ".f")
        if not os.path.exists(file_name):
            print("[" + self._pt_definition.comp_name + "-" + self._pt_definition.pt_type.name + "]" + " AllSMT formula is not in cache, performing AllSMT...", end= "\x1b[1K\r")
            formula = allsmt(self._behaviour_formula, self.fault_atoms + self._concretizer.input_ports + self._abstractor.output_ports)
            print("[" + self._pt_definition.comp_name + "-" + self._pt_definition.pt_type.name + "]" + " Create dummy AllSMT formula and save it in cache...", end= "\x1b[1K\r")
            dummy_qe_formula = formula.serialize()
            for idx, f_atom in enumerate(self._fault_atoms):
                dummy_qe_formula = dummy_qe_formula.replace(f_atom.serialize(), "$EMPTY_F$" + str(idx))
            dummy_qe_formula = dummy_qe_formula.replace(self._pt_definition.pt_type.name, self._pt_definition.pt_type.name)
            dummy_qe_formula = dummy_qe_formula.replace(self._pt_definition.comp_name, "$EMPTY$")
            # Print formula on file
            with open(file_name, "w") as cache_file:
                cache_file.write(dummy_qe_formula)

        else:
            print("[" + self._pt_definition.comp_name + "-" + self._pt_definition.pt_type.name + "]" + " Formula found in cache")
            # Import formula from cache
            with open(file_name, "r") as cache_file:
                dummy_qe_formula_str = cache_file.read()
            # Parse string and extract SMT formula
            print("[" + self._pt_definition.comp_name + "-" + self._pt_definition.pt_type.name + "]" + " Parsing...", end="\r")
            formula_str = dummy_qe_formula_str.replace("$EMPTY$", self._pt_definition.comp_name)
            for idx, f_atom in enumerate(self._fault_atoms):
                formula_str = formula_str.replace("$EMPTY_F$" + str(idx), f_atom.serialize())
            formula_str = formula_str.replace(self._pt_definition.pt_type.name, self._pt_definition.pt_type.name)
            formula = parse(formula_str)
            print("[" + self._pt_definition.comp_name + "-" + self._pt_definition.pt_type.name + "]" + " Imported!")
            # Check
            # with Solver("z3") as solver:
            #    print(solver.is_sat(Not(Implies(self._behaviour_formula, formula))))
        return formula

    @property
    def comp_n_inputs(self):
        return self._comp_n_inputs


class Concretizer(Component):
    """
    Class representing a concretizer
    """
    def __init__(self, name: str, comp_n_inputs: int, stage: Stage):
        """
        Given a stage, it creates its concretizer
        :param name: name of the component
        :param comp_n_inputs: number of inputs of the nominal component
        :param stage: stage where the concretizer has to be applied
        """
        # output ports correspond to the input ports of the stage
        self._output_pattern_ports = stage.pattern.input_ports
        self._output_comp_ports = stage.nominal_module.input_ports
        output_ports = self._output_comp_ports + self._output_pattern_ports
        # Create input ports
        input_ports = []
        #  [[i0,i2,i4],[i1,i3,i5]]
        self._indexed_in_ports = [[] for idx in range(comp_n_inputs)]
        i = 0
        for module in stage.pattern.modules:
            assert len(module.input_ports) == comp_n_inputs
            for p_idx, ip in enumerate(module.input_ports):
                port = Symbol(name + ".i" + str(i))
                input_ports.append(port)
                self._indexed_in_ports[p_idx].append(port)
                i = i + 1
        super(Concretizer, self).__init__(name, ComponentType.CONCRETIZER, input_ports, output_ports)

        # TODO: check this:
        #  the number of pattern's inputs should be a multiple of the number of the component's inputs
        assert len(stage.pattern.input_ports) % len(
            stage.nominal_module.input_ports) == 0, "[Concretizer] Incompatible number of pattern's inputs and component's inputs"
        # NOTICE! component's inputs and pattern's input have to have the same index!
        out_constraints = []
        for idx, patt_port in enumerate(self._output_pattern_ports):
            out_constraints.append(
                Iff(
                    self._input_ports[idx],
                    Equals(
                        patt_port,
                        self._output_comp_ports[idx % len(self._output_comp_ports)]
                    )
                )
            )
        self._behaviour_formula = And(out_constraints)

    @property
    def indexed_in_ports(self):
        return self._indexed_in_ports


class Abstractor(Component):
    """
    Class representing an Abstractor component
    """

    def __init__(self, name: str, stage: Stage):
        """
        Given a stage it creates an abstractor
        :param name: name of the component
        :param stage: stage where the abstractor has to be applied
        """
        # Define input and output ports
        output_ports = [Symbol(name + ".o" + str(idx)) for idx in range(len(stage.pattern.output_ports))]
        self._input_comp_port = stage.nominal_module.output_ports[0]
        self._input_pattern_ports = stage.pattern.output_ports
        input_ports = [self._input_comp_port] + self._input_pattern_ports
        super(Abstractor, self).__init__(name, ComponentType.ABSTRACTOR, input_ports, output_ports)

        out_constraints = []
        for idx, patt_port in enumerate(self._input_pattern_ports):
            out_constraints.append(
                Iff(
                    Equals(
                        patt_port,
                        self._input_comp_port
                    ),
                    self._output_ports[idx]
                )
            )
        self._behaviour_formula = And(out_constraints)


'''# Test - Example
from patterns import TmrV111Definition
if __name__ == "__main__":
    c = Csa(TmrV111Definition("C1", "TMR_V111", 3, [Symbol("F0"),Symbol("F1"),Symbol("F2")], Symbol("F3")))
    print(c.behaviour_formula.serialize())
    print(c.get_update_available_ports())
    print(c.get_update_available_ports())
    print(c.get_update_available_ports())
# # (((((! F0) -> (C1.TMR_V111.M0.o0 = C1_nom.beh(C1.TMR_V111.M0.i0, C1.TMR_V111.M0.i1))) & 
# # ((! F1) -> (C1.TMR_V111.M1.o0 = C1_nom.beh(C1.TMR_V111.M1.i0, C1.TMR_V111.M1.i1))) & 
# # ((! F2) -> (C1.TMR_V111.M2.o0 = C1_nom.beh(C1.TMR_V111.M2.i0, C1.TMR_V111.M2.i1))) & 
# # ((! F3) -> (((C1.TMR_V111.M0.o0 = C1.TMR_V111.M1.o0) | (C1.TMR_V111.M0.o0 = C1.TMR_V111.M2.o0)) ? (C1.TMR_V111.V.o0 = C1.TMR_V111.M0.o0) : ((C1.TMR_V111.M1.o0 = C1.TMR_V111.M2.o0) -> (C1.TMR_V111.V.o0 = C1.TMR_V111.M1.o0))))) & 
# # (C1_nom.o0 = C1_nom.beh(C1_nom.i0, C1_nom.i1))) & 
# # (('[C1-TMR_V111].concr.i0' <-> (C1.TMR_V111.M0.i0 = C1_nom.i0)) & 
# # ('[C1-TMR_V111].concr.i1' <-> (C1.TMR_V111.M0.i1 = C1_nom.i1)) & 
# # ('[C1-TMR_V111].concr.i2' <-> (C1.TMR_V111.M1.i0 = C1_nom.i0)) & 
# # ('[C1-TMR_V111].concr.i3' <-> (C1.TMR_V111.M1.i1 = C1_nom.i1)) & 
# # ('[C1-TMR_V111].concr.i4' <-> (C1.TMR_V111.M2.i0 = C1_nom.i0)) & 
# # ('[C1-TMR_V111].concr.i5' <-> (C1.TMR_V111.M2.i1 = C1_nom.i1))) & 
# # ((C1.TMR_V111.V.o0 = C1_nom.o0) <-> '[C1-TMR_V111].abstr.o0'))'''
