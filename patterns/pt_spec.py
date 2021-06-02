from params import NonFuncParams
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

'''
Duplex
'''
    
class DpxSpec(PatternSpec):
    def __init__(self, name, modules_params: list, comparator_param: NonFuncParams):
        '''
        Create a specification of a DPX
        :param modules_probs: list of length 2 containing the probabilities of the 2 modules
        :param voter_probs: fault probability of the comparator
        '''
        self._modules_params = modules_params
        self._comparator_params = comparator_param
        super(DpxSpec, self).__init__(PatternType.DPX_HM, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def comparator_param(self):
        return self._comparator_param
    

'''
TMR
'''
            
class TmrV001Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V001
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 3 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV001Spec, self).__init__(PatternType.TMR_V001, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params


class TmrV010Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V010
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 3 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV010Spec, self).__init__(PatternType.TMR_V010, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params
    

class TmrV011Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V011
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 3 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV011Spec, self).__init__(PatternType.TMR_V011, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params
        

class TmrV012Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V012
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 2 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV012Spec, self).__init__(PatternType.TMR_V012, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params
        

class TmrV100Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V100
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 3 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV100Spec, self).__init__(PatternType.TMR_V100, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params
    

class TmrV101Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V101
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 3 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV101Spec, self).__init__(PatternType.TMR_V101, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params
    

class TmrV102Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V103
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 2 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV102Spec, self).__init__(PatternType.TMR_V102, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params
    
    
class TmrV110Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V110
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 3 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV110Spec, self).__init__(PatternType.TMR_V110, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params                    


class TmrV111Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_param: NonFuncParams):
        '''
        Create a specification of a TMR-V111
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the voter
        '''
        self._modules_params = modules_params
        self._voter_param = voter_param
        super(TmrV111Spec, self).__init__(PatternType.TMR_V111, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_param(self):
        return self._voter_param


class TmrV111x3Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V111
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 3 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV111x3Spec, self).__init__(PatternType.TMR_V111x3, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params


class TmrV112Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V112
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 2 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV112Spec, self).__init__(PatternType.TMR_V112, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params
  

class TmrV120Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V120
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 2 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV120Spec, self).__init__(PatternType.TMR_V120, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params  
  

class TmrV122Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V122
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 2 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV122Spec, self).__init__(PatternType.TMR_V122, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params  


class TmrV123Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_params: list):
        '''
        Create a specification of a TMR-V123
        :param modules_probs: list of length 3 containing the probabilities of the 3 modules
        :param voter_probs: fault probability of the 3 voters
        '''
        self._modules_params = modules_params
        self._voter_params = voter_params
        super(TmrV123Spec, self).__init__(PatternType.TMR_V123, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_params(self):
        return self._voter_params  


'''
X-o-o-Y
'''

class XooY_3oo4Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_param: NonFuncParams):
        '''
        Create a specification of a 3-o-o-4
        :param modules_probs: list of length 4 containing the probabilities of the 4 modules
        :param voter_probs: fault probability of the voter
        '''
        self._modules_params = modules_params
        self._voter_param = voter_param
        super(XooY_3oo4Spec, self).__init__(PatternType.XooY_3oo4, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_param(self):
        return self._voter_param


class XooY_3oo5Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_param: NonFuncParams):
        '''
        Create a specification of a 3-o-o-5
        :param modules_probs: list of length 5 containing the probabilities of the 5 modules
        :param voter_probs: fault probability of the voter
        '''
        self._modules_params = modules_params
        self._voter_param = voter_param
        super(XooY_3oo5Spec, self).__init__(PatternType.XooY_3oo5, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_param(self):
        return self._voter_param


class XooY_4oo6Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_param: NonFuncParams):
        '''
        Create a specification of a 4-o-o-6
        :param modules_probs: list of length 6 containing the probabilities of the 6 modules
        :param voter_probs: fault probability of the voter
        '''
        self._modules_params = modules_params
        self._voter_param = voter_param
        super(XooY_4oo6Spec, self).__init__(PatternType.XooY_4oo6, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_param(self):
        return self._voter_param


class XooY_4oo7Spec(PatternSpec):
    def __init__(self, name, modules_params: list, voter_param: NonFuncParams):
        '''
        Create a specification of a 4-o-o-7
        :param modules_probs: list of length 7 containing the probabilities of the 7 modules
        :param voter_probs: fault probability of the voter
        '''
        self._modules_params = modules_params
        self._voter_param = voter_param
        super(XooY_4oo7Spec, self).__init__(PatternType.XooY_4oo7, name)

    @property
    def modules_params(self):
        return self._modules_params

    @property
    def voter_param(self):
        return self._voter_param