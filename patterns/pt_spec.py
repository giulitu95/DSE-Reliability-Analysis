from params import NonFuncParamas
from patterns import PatternType



class PatternSpec:
    def __init__(self, pattern_type, name):
        self._pt_type = pattern_type
        self._name = name

    @property
    def pt_type(self):
        return self._pt_type

    @property
    def name(self):
        return self._name

class TmrV111Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: NonFuncParamas):
        '''
        Create a specification of a TMR-V111
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        '''
        super(TmrV111Spec, self).__init__(PatternType.TMR_V111, name)
    pass


class Tmr123Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: list):
        '''
        Create a specification of a TMR-V123
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voters_probs: list of length 3 containing the probabidlities of the 3 voters
        '''
        super(Tmr123Spec, self).__init__(PatternType.TMR_V123)
    pass