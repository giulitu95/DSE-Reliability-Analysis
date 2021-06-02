from enum import Enum


class ComponentType(Enum):
    """
    Enum which determines the type of component (e.g. BASIC, VOTER...)
    """
    BASIC = 1
    VOTER = 2
    PATTERN = 3
    STAGE = 4
    CONCRETIZER = 5,
    ABSTRACTOR = 6
    CSA = 7
    TLE = 8
    COMPARATOR = 9


class Component:
    """
    Class representing a generic component
    """
    _behaviour_formula = None

    def __init__(self, name: str, comp_type: ComponentType, input_ports: list, output_ports: list, fault_atoms=None):
        '''
        Creates a generic component
        :param name: name of the component
        :param comp_type: type of the component (ComponentType)
        :param input_ports: a list of symbols corresponding the input ports
        :param output_ports: a list of symbols corresponding the output ports
        :param fault_atoms: a ;ost pf symbols corresponding to the fault atoms of the component
        '''
        if fault_atoms is None:
            fault_atoms = []
        self._name = name
        self._comp_type = comp_type
        self._input_ports = input_ports
        self._output_ports = output_ports
        if fault_atoms is None: self._fault_atoms = []
        else: self._fault_atoms = fault_atoms

    @property
    def behaviour_formula(self):
        """
        Retrieves the SMT formula representing the behaviour of the component
        Returns: SMT formula

        """
        # Each component has to have an internal behaviour
        assert self._behaviour_formula is not None, "Behaviour formula does not exist for this component"
        return self._behaviour_formula

    @property
    def input_ports(self):
        """
        Returns: a list of symbols corresponding to the input ports of the component
        """
        return self._input_ports

    @property
    def output_ports(self):
        """
        Returns: a list of symbols corresponding to the output ports of the component
        """
        return self._output_ports

    @property
    def fault_atoms(self):
        """
        Returns: a list of fault atoms associated to that component
        :return:
        """
        return self._fault_atoms

    @property
    def name(self):
        return self._name