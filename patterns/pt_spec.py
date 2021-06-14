from params import NonFuncParamas
from patterns import PatternType
import patterns.tmr_v111 as tmr_v111
import patterns.tmr_v123 as tmr_v123

__author__ = "Giuliano Turri, Antonio Tierno"


class PatternSpec:
    def __init__(self, pattern_type, pattern_class, param_list):
        self._pt_type = pattern_type
        self._pt_class = pattern_class
        self._param_list = param_list
    @property
    def pt_type(self):
        return self._pt_type

    @property
    def pt_class(self):
        return self._pt_class

    @property
    def param_list(self):
        return self._param_list


class TmrV111Spec(PatternSpec):
    def __init__(self, modules_params: list, voter_params: NonFuncParamas):
        """
        Create a specification of a TMR-V111
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voter_param = voter_params
        super(TmrV111Spec, self).__init__(PatternType.TMR_V111, tmr_v111.TmrV111, modules_params + [voter_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_param(self):
        return self._voter_param


class TmrV123Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: list):
        """
        Create a specification of a TMR-V111
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV123Spec, self).__init__(PatternType.TMR_V123, tmr_v123.TmrV123, modules_params + voters_params)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params



