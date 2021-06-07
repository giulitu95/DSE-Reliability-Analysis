from params import NonFuncParamas
from patterns import PatternType

__author__ = "Giuliano Turri"

class PatternSpec:
    def __init__(self, pattern_type):
        self._pt_type = pattern_type

    @property
    def pt_type(self):
        return self._pt_type




class TmrV111Spec(PatternSpec):
    def __init__(self, modules_params: list, voter_param: NonFuncParamas):
        '''
        Create a specification of a TMR-V111
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        '''
        self._modules_params = modules_params
        self._voter_param = voter_param
        super(TmrV111Spec, self).__init__(PatternType.TMR_V111)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_param(self):
        return self._voter_param



