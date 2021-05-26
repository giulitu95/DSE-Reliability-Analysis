from components.component import Component, ComponentType
from enum import Enum


class PatternType(Enum):
    """
    Enum which determines the type of pattern (e.g. TMR_V111, TRM_V123, DPX...)
    """
    TMR_V111 = 1
    TMR_V123 = 2
    # ...


class Pattern(Component):
    """
    Class representing a general pattern
    """
    def __init__(self, name: str, pattern_type: PatternType, fault_atoms: list, input_ports: list, output_ports: list):
        """
        Create a generic pattern
        :param name: name of the instance of the pattern
        :param pattern_type: type of pattern
        :param fault_atoms: list of available fault atoms for that pattern
        :param input_ports: list of symbols corresponding to the input ports
        :param output_ports: list of symbols corresponding to the output ports
        """
        super(Pattern, self).__init__(name, ComponentType.PATTERN, input_ports, output_ports, fault_atoms=fault_atoms)
        self._pattern_type = pattern_type
