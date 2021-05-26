from component import Component, ComponentType
from module import Module
from patterns.pt_spec import PtType
from pysmt.shortcuts import *


class Stage(Component):

    def __init__(self, comp_name: str, comp_n_inputs: int, pt_type: PtType, fault_atoms: list):
        '''
        Create a Stage given a component and a pattern
        :param comp_name: name of the component
        :param comp_n_inputs: number of inputs of the basic component
        :param pt_type: type of pattern
        :param fault_atoms: list of available fault atoms
        '''
        pass
