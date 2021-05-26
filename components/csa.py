from patterns.pt_spec import PtType
from component import ComponentType, Component


class Csa:
    '''
    Class providing methods and attribute to compute the formula which represents the sequential composition of
    components Concretizer - Stage - Abstractor
    '''
    def __init__(self, comp_name: str, comp_n_inputs: int, pt_type: PtType, fault_atoms: list):
        '''
        Create a CSA
        :param comp_name: name of the component
        :param comp_n_inputs: number of inputs of the basic component
        :param pt_type: type of pattern
        :param fault_atoms: list of available fault atoms
        '''
        pass


class Concretizer(Component):
    '''
    Class representing a Concretizer component
    '''
    def __init__(self, name: str, n_inputs: int):
        '''
        Create a concretizer
        :param name: concretizer's name
        :param n_inputs: number of concretizer's inputs
        '''

class Abstractor(Component):
    '''
    Class representing an Abstractor component
    '''
    def __init__(self, name: str, n_inputs: int):
        '''
        Crewate an abstractor
        :param name: abstractor's name
        :param n_inputs: number of abstractor's inputs
        '''
