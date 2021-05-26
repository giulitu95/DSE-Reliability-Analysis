from components.component import Component, ComponentType
from pysmt.shortcuts import *


class Module(Component):

    def __init__(self, name: str, n_inputs: int):
        '''
        Create a new Module
        :param name: module's name
        :param n_inputs: number of module's inputs
        '''