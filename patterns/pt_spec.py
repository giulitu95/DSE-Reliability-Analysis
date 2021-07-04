from params import NonFuncParamas
from patterns import PatternType
import patterns.plain as plain
import patterns.cmp as cmp
import patterns.tmr_v111 as tmr_v111
import patterns.tmr_v001 as tmr_v001
import patterns.tmr_v010 as tmr_v010
import patterns.tmr_v100 as tmr_v100
import patterns.tmr_v011 as tmr_v011
import patterns.tmr_v101 as tmr_v101
import patterns.tmr_v110 as tmr_v110
import patterns.tmr_v122 as tmr_v122
import patterns.tmr_v112 as tmr_v112
import patterns.tmr_v120 as tmr_v120
import patterns.tmr_v102 as tmr_v102
import patterns.tmr_v012 as tmr_v012
import patterns.tmr_v123 as tmr_v123
import patterns.xooy_3oo4 as xooy_3oo4
#3oo5
#4oo5
#4oo6


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


# === PLAIN ===
class PlainSpec(PatternSpec):
    def __init__(self, module_params: NonFuncParamas):
        self._module_params = module_params
        super(PlainSpec, self).__init__(PatternType.PLAIN, plain.Plain, [self._module_params])

    @property
    def module_params(self):
        return self._module_params

# === CMP ===
class CmpSpec(PatternSpec):
    def __init__(self, modules_params: list, comparator_params: NonFuncParamas):
        """
        Create a specification of a CMP
        :param modules_probs: list of length 2 containing the probabilities of the 2 modules
        :param voter_probs: fault probability of the comparator
        """

        self._modules_params = modules_params
        self._comparator_param = comparator_params
        super(CmpSpec, self).__init__(PatternType.CMP, cmp.Comparator, modules_params + [comparator_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def comparator_param(self):
        return self._comparator_param

# === TMR_V111 ===
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

# === TMR_V001 ===
class TmrV001Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V001
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV001Spec, self).__init__(PatternType.TMR_V001, tmr_v001.TmrV001, modules_params + [voters_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V010 ===
class TmrV010Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V010
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV010Spec, self).__init__(PatternType.TMR_V010, tmr_v010.TmrV010, modules_params + [voters_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V100 ===
class TmrV100Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V100
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV100Spec, self).__init__(PatternType.TMR_V100, tmr_v100.TmrV100, modules_params + [voters_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V011 ===
class TmrV011Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V010
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voters
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV011Spec, self).__init__(PatternType.TMR_V011, tmr_v011.TmrV011, modules_params + [voters_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V101 ===
class TmrV101Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V010
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV101Spec, self).__init__(PatternType.TMR_V101, tmr_v101.TmrV101, modules_params + [voters_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V110 ===
class TmrV110Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V110
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voters
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV110Spec, self).__init__(PatternType.TMR_V110, tmr_v110.TmrV110, modules_params + [voters_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V122 ===
class TmrV122Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V122
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV122Spec, self).__init__(PatternType.TMR_V122, tmr_v122.TmrV122, modules_params + voters_params)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V112 ===
class TmrV112Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V112
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV112Spec, self).__init__(PatternType.TMR_V112, tmr_v122.TmrV112, modules_params + voters_params)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V120 ===
class TmrV120Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V012
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV120Spec, self).__init__(PatternType.TMR_V120, tmr_v120.TmrV120, modules_params + voters_params)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V102 ===
class TmrV102Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: list):
        """
        Create a specification of a TMR-V012
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV102Spec, self).__init__(PatternType.TMR_V102, tmr_v102.TmrV102, modules_params + voters_params)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V012 ===
class TmrV012Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V012
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(TmrV012Spec, self).__init__(PatternType.TMR_V012, tmr_v012.TmrV012, modules_params + voters_params)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params

# === TMR_V123 ===
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

# === XooY_3oo4 ===
class Xooy3oo4Spec(PatternSpec):
    def __init__(self, modules_params: list, voters_params: NonFuncParamas):
        """
        Create a specification of a TMR-V111
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        """
        self._modules_params = modules_params
        self._voters_params = voters_params
        super(Xooy3oo4Spec, self).__init__(PatternType.Xooy_3oo4, xooy_3oo4.Xooy_3oo4, modules_params + [voters_params])

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voters_params(self):
        return self._voters_params