from patterns import PatternType, PatternDefinition 
from patterns.dpx_hm import Dpx_hm, Dpx_hm_Definition
from patterns.tmr_v001 import TmrV001, TmrV001Definition
from patterns.tmr_v010 import TmrV010, TmrV010Definition
from patterns.tmr_v011 import TmrV011, TmrV011Definition
from patterns.tmr_v012 import TmrV012, TmrV012Definition
from patterns.tmr_v100 import TmrV100, TmrV100Definition
from patterns.tmr_v101 import TmrV101, TmrV101Definition
from patterns.tmr_v102 import TmrV102, TmrV102Definition
from patterns.tmr_v110 import TmrV110, TmrV110Definition
from patterns.tmr_v111 import TmrV111, TmrV111Definition
from patterns.tmr_v111x3 import TmrV111x3, TmrV111x3Definition
from patterns.tmr_v112 import TmrV112, TmrV112Definition
from patterns.tmr_v120 import TmrV120, TmrV120Definition
from patterns.tmr_v122 import TmrV122, TmrV122Definition
from patterns.tmr_v123 import TmrV123, TmrV123Definition
from patterns.xooy_3oo4 import XooY_3oo4, XooY_3oo4_Definition
from patterns.xooy_3oo5 import XooY_3oo5, XooY_3oo5_Definition
from patterns.xooy_4oo6 import XooY_4oo6, XooY_4oo6_Definition
from patterns.xooy_4oo7 import XooY_4oo7, XooY_4oo7_Definition
from components.csa import Csa
from pysmt.shortcuts import *
import math

class ArchNode:
    """
    Class provinding the methods for creating the formulas associated to a specific component of the architecture
    """
    def __init__(self, pt_library: list, comp_name: str, n_predecessors, next_archnodes: list = None):
        """
        Create an Architecture Node
        :param pt_library: list of pattern type
        :param comp_name: name of component
        :param next_archnodes: list of ArchNode instances indicating the component connected to the current one
        :param n_predecessors: number of predecessor components which are linked to the current node
        """
        # Check the pattern which requires the highest number of fault atoms:
        self._max_n_f = 0
        for pt in pt_library:
            if pt.pt_type == PatternType.DPX_HM:
                if self._max_n_f < Dpx_hm.n_f_atoms:
                    self._max_n_f = Dpx_hm.n_f_atoms            
            elif pt.pt_type == PatternType.TMR_V001:
                if self._max_n_f < TmrV001.n_f_atoms:
                    self._max_n_f = TmrV001.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V010:
                if self._max_n_f < TmrV010.n_f_atoms:
                    self._max_n_f = TmrV010.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V011:
                if self._max_n_f < TmrV011.n_f_atoms:
                    self._max_n_f = TmrV011.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V012:
                if self._max_n_f < TmrV012.n_f_atoms:
                    self._max_n_f = TmrV012.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V100:
                if self._max_n_f < TmrV100.n_f_atoms:
                    self._max_n_f = TmrV100.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V101:
                if self._max_n_f < TmrV101.n_f_atoms:
                    self._max_n_f = TmrV101.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V102:
                if self._max_n_f < TmrV102.n_f_atoms:
                    self._max_n_f = TmrV102.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V110:
                if self._max_n_f < TmrV110.n_f_atoms:
                    self._max_n_f = TmrV110.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V111:
                if self._max_n_f < TmrV111.n_f_atoms:
                    self._max_n_f = TmrV111.n_f_atoms                  
            elif pt.pt_type == PatternType.TMR_V111:
                if self._max_n_f < TmrV111x3.n_f_atoms:
                    self._max_n_f = TmrV111x3.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V112:
                if self._max_n_f < TmrV112.n_f_atoms:
                    self._max_n_f = TmrV112.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V120:
                if self._max_n_f < TmrV120.n_f_atoms:
                    self._max_n_f = TmrV120.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V122:
                if self._max_n_f < TmrV122.n_f_atoms:
                    self._max_n_f = TmrV122.n_f_atoms
            elif pt.pt_type == PatternType.TMR_V123:
                if self._max_n_f < TmrV123.n_f_atoms:
                    self._max_n_f = TmrV123.n_f_atoms
            elif pt.pt_type == PatternType.XooY_3oo4:
                if self._max_n_f < XooY_3oo4.n_f_atoms:
                    self._max_n_f = XooY_3oo4.n_f_atoms
            elif pt.pt_type == PatternType.XooY_3oo5:
                if self._max_n_f < XooY_3oo5.n_f_atoms:
                    self._max_n_f = XooY_3oo5.n_f_atoms
            elif pt.pt_type == PatternType.XooY_4oo6:
                if self._max_n_f < XooY_4oo6.n_f_atoms:
                    self._max_n_f = XooY_4oo6.n_f_atoms
            elif pt.pt_type == PatternType.XooY_4oo7:
                if self._max_n_f < XooY_4oo7.n_f_atoms:
                    self._max_n_f = XooY_4oo7.n_f_atoms                                                                
            else:
                NotImplementedError()

        # create list of available fault atoms
        self._fault_atoms = [Symbol(comp_name + "_F" + str(idx)) for idx in range(self._max_n_f)]
        # prepare configuration atoms
        if len(pt_library) > 1:
            n_conf_atoms = math.ceil(math.log(len(pt_library), 2))
        else:
            n_conf_atoms = 1
            
        # List of configuration atoms for this CSA
        self._conf_atoms = [Symbol("CONF_" + comp_name + "[" + str(idx) +"]") for idx in range(n_conf_atoms)]
        # check invalid configurations
        invalid_conf = []
        for idx in range(len(pt_library), (2 ** n_conf_atoms)):
            bin_str = '{0:0{l}b}'.format(idx, l = len(self._conf_atoms))
            conf = []
            for i, bin_ in enumerate(bin_str):
                if bin_ == '0': conf.append(Not(self._conf_atoms[i]))
                else: conf.append(self._conf_atoms[i])
            invalid_conf.append(And(conf))
        self._conf_formula = And( # Here we exclude invalid configurations
            Not(Or(invalid_conf))
        )
        self._csa_list = []
        self._f_atoms2prob = {}
        prob_constraints = []
        
        # create probability symbols (real)
        for f_idx, f_atom in enumerate(self._fault_atoms):
            self._f_atoms2prob[f_atom] = Symbol("p" + str(f_idx) + "_" + comp_name, REAL)

        # - prepare list of CSA for each possible pattern-combination
        # - assign non functional parameters to the probability symbols
        for idx, pt in enumerate(pt_library):
            conf = self.get_conf_by_index(idx)
            
            # --- DPX ---
            if pt.pt_type == PatternType.DPX_HM:
                # create CSA
                pt_def = Dpx_hm_Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:2], self._fault_atoms[1])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:2]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # comparator:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[1]], Real(pt.comparator_param.fault_prob))
                    )
                )
            
            # --- TMR_V001 ---
            elif pt.pt_type == PatternType.TMR_V001:
                # create CSA
                pt_def = TmrV001Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )
            
            # --- TMR_V010 ---
            elif pt.pt_type == PatternType.TMR_V011:
                # create CSA
                pt_def = TmrV010Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )

            # --- TMR_V011 ---
            elif pt.pt_type == PatternType.TMR_V011:
                # create CSA
                pt_def = TmrV011Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )
            
            # --- TMR_V012 ---
            elif pt.pt_type == PatternType.TMR_V011:
                # create CSA
                pt_def = TmrV012Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voters:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:4]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                                    
            # --- TMR_V100 ---
            elif pt.pt_type == PatternType.TMR_V100:
                # create CSA
                pt_def = TmrV100Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )
            
            # --- TMR_V101 ---
            elif pt.pt_type == PatternType.TMR_V101:
                # create CSA
                pt_def = TmrV101Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )

            # --- TMR_V102 ---
            elif pt.pt_type == PatternType.TMR_V102:
                # create CSA
                pt_def = TmrV102Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voters:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:4]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )
                    
            # --- TMR_V110 ---
            elif pt.pt_type == PatternType.TMR_V110:
                # create CSA
                pt_def = TmrV110Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )
                                                                                
            # --- TMR_V111 ---
            elif pt.pt_type == PatternType.TMR_V111:
                # create CSA
                pt_def = TmrV111Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )

            # --- TMR_V111x3 ---
            elif pt.pt_type == PatternType.TMR_V111x3:
                # create CSA
                pt_def = TmrV111x3Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[3]], Real(pt.voter_param.fault_prob))
                    )
                )
                
            # --- TMR_V112 ---
            elif pt.pt_type == PatternType.TMR_V112:
                # create CSA
                pt_def = TmrV112Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voters:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:4]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )

            # --- TMR_V120 ---
            elif pt.pt_type == PatternType.TMR_V120:
                # create CSA
                pt_def = TmrV120Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voters:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:4]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )

            # --- TMR_V122 ---
            elif pt.pt_type == PatternType.TMR_V122:
                # create CSA
                pt_def = TmrV122Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voters:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:4]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )                    

            # --- TMR_V123 ---
            elif pt.pt_type == PatternType.TMR_V123:
                # create CSA
                pt_def = TmrV123Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:3], self._fault_atoms[3])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:3]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voters:
                for f_idx, f_atom in enumerate(self._fault_atoms[3:5]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.voters_params[f_idx].fault_prob)))
                    )

            # --- 3-o-o-4 ---
            elif pt.pt_type == PatternType.XooY_3oo4:
                # create CSA
                pt_def = XooY_3oo4_Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:4], self._fault_atoms[4])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:4]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[4]], Real(pt.voter_param.fault_prob))
                    )
                )

            # --- 3-o-o-5 ---
            elif pt.pt_type == PatternType.XooY_3oo5:
                # create CSA
                pt_def = XooY_3oo5_Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:5], self._fault_atoms[5])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:5]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[5]], Real(pt.voter_param.fault_prob))
                    )
                )                
 
            # --- 4-o-o-6 ---
            elif pt.pt_type == PatternType.XooY_4oo6:
                # create CSA
                pt_def = XooY_4oo6_Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:6], self._fault_atoms[6])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:6]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[6]], Real(pt.voter_param.fault_prob))
                    )
                )       

            # --- 4-o-o-7 ---
            elif pt.pt_type == PatternType.XooY_4oo7:
                # create CSA
                pt_def = XooY_4oo7_Definition(comp_name, pt.name, n_predecessors, self._fault_atoms[:7], self._fault_atoms[7])
                csa = Csa(pt_def)
                self._csa_list.append(csa)
                # assign non functional parameters to the probability symbols associated to each fault atoms
                # modules:
                for f_idx, f_atom in enumerate(self._fault_atoms[:7]):
                    prob_constraints.append(
                        Implies(
                            conf,
                            Equals(self._f_atoms2prob[f_atom], Real(pt.modules_params[f_idx].fault_prob)))
                    )
                # voter:
                prob_constraints.append(
                    Implies(
                        conf,
                        Equals(self._f_atoms2prob[self._fault_atoms[7]], Real(pt.voter_param.fault_prob))
                    )
                ) 
                
        self._prob_constraints = And(prob_constraints)

        # Constraints which describe the connections between components
        self._linker_constr = None
        # They express whether a pattern (configuration) can be linked to another pattern (configuration)
        self._compatibility_constr = None
        if next_archnodes is not None:
            # link the CSA of the current node with the CSA of the next node
            linker_constr = []
            compatibility_constr = []
            for c_idx, current_csa in enumerate(self._csa_list):
                # iterate over the current CSA
                comp2comp_constr = []
                conf = self.get_conf_by_index(c_idx)
                for next_node in next_archnodes:
                    # iterate over the next Archnodes
                    for n_idx, next_csa in enumerate(next_node.csa_list):
                        # iterate over the csa of the next Archnode
                        if len(current_csa.output_ports) == 1:
                            # if the CSA has only one output, then it can be connected with every next CSA
                            to_connect_ports = next_csa.get_update_available_ports()
                            for in_port in to_connect_ports:
                                comp2comp_constr.append(Iff(current_csa.output_ports[0], in_port))
                        elif len(current_csa.output_ports) == next_csa.comp_n_inputs:
                            # if 2 CSA have compatible outputs-inputs then, they can be connected together
                            to_connect_ports = next_csa.get_update_available_ports()
                            for idx in range(len(to_connect_ports)):
                                comp2comp_constr.append(Iff(current_csa.output_ports[idx], next_csa.input_ports[idx]))
                        else:
                            # patterns are not sequentially compatible so, add the formula
                            # current_configuration -> ~next_configuration
                            compatibility_constr.append(Implies(conf, Not(next_node.get_conf_by_index(n_idx))))
                        next_csa.reset_available_ports()
                linker_constr.append(
                    Implies(
                        conf,
                        And(comp2comp_constr)
                    )
                )
            self._linker_constr = And(linker_constr)
            self._compatibility_constr = And(compatibility_constr)
        else:
            # It is the last node! (TLE)
            pass

    def get_qe_formulas(self) -> list:
        """
        Retrieve a list of boolean formula obtained applying AllSMT to every
        :return: the list of boolean formula for each csa
        """
        formulas = []
        for csa in self._csa_list:
            formulas.append(csa.get_qe_formula())
        return formulas

    def get_conf_by_index(self, index: int):
        """
        Given an index retrieve a formula representing that configuration
        :param index: index
        :return: Boolean formula in DNF which describe the configuration
        """
        bin_str = '{0:0{l}b}'.format(index, l = len(self._conf_atoms))
        conf = []
        for i, bin_ in enumerate(bin_str):
            if bin_ == '0': conf.append(Not(self._conf_atoms[i]))
            else: conf.append(self._conf_atoms[i])
        return And(conf)

    @property
    def csa_list(self) -> list:
        """
        :return: list of csa of the node
        """
        return self._csa_list

    @property
    def linker_constr(self):
        """
        :return: Formula representing the connections between the various csa
        """
        return self._linker_constr

    @property
    def compatibility_constr(self):
        """
        :return: Formula representing the available connections between CSA
        """
        return self._compatibility_constr

    @property
    def conf_formula(self):
        """
        :return: Formula representing the available configurations
        """
        return self._conf_formula

    @property
    def prob_constraints(self):
        """
        :return: A formula which assigns to each probability symbol a value (depending on configuration)
        """
        return self._prob_constraints

    @property
    def f_atoms2prob(self):
        """
        :return: A map which for every fault atom it's assiciated a probability real symbol
        """
        return self._f_atoms2prob

    @property
    def conf_atoms(self):
        """
        :return: The list of configuration atoms
        """
        return self._conf_atoms

    @property
    def fault_atoms(self):
        """
        :return: The list of fault atoms
        """
        return self._fault_atoms

'''# Test - Example
from patterns import TmrV111Spec
from params import NonFuncParamas
if __name__ == "__main__":
    an4 = ArchNode([TmrV111Spec("TMR_V111_A",
                                [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                                NonFuncParamas(0.1))], "C4", 3)
    an1 = ArchNode([TmrV111Spec("TMR_V111_A", [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)], NonFuncParamas(0.1))], "C1", 1, next_archnodes=[an4])
    an2 = ArchNode([TmrV111Spec("TMR_V111_A",[NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],NonFuncParamas(0.1))], "C2", 1, next_archnodes=[an4])
    an3 = ArchNode([TmrV111Spec("TMR_V111_A",
                                [NonFuncParamas(0.1), NonFuncParamas(0.2), NonFuncParamas(0.02), NonFuncParamas(0.1)],
                                NonFuncParamas(0.1))], "C3", 1, next_archnodes=[an4])



    qe1 = an1.get_qe_formulas()
    qe2 = an2.get_qe_formulas()'''


