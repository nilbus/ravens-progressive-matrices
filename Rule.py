from FigureDiff import FigureDiff

class Rule:
    def __init__(self, before, after):
        self.before = before
        self.after = after
        self.figure_diff = FigureDiff(before, after)

    def __repr__(self):
        return "<Rule figure_diff: %s>" % (self.figure_diff,)

    def similarity_to(self, other):
        '''
        Score similarity to another Rule, based on figure_diff similarity.
        @return a numeric score from 0 to 1, where 1.0 represents equality
        '''
        return self.figure_diff.similarity_to(other.figure_diff)
