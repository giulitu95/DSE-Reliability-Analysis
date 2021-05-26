from components.component import Component, ComponentType
from pysmt.shortcuts import *


class Voter(Component):
    # TODO: generalize the voter with more then 3 real inputs?
    def __init__(self, name: str, faulty_atom: Symbol):
        '''
        Create a voter
        :param name: name of voter
        :param faulty_atom: symbol used to indicate whether the voter is faulty
        '''
        self._name = name
        self._faulty_atom = faulty_atom