class Rule:
    @classmethod
    def identity(cls):
        return cls()

    def __init__(self):
        pass

    def similarity_to(self, other):
        '''TODO'''
        return 1.0
