from FigureDiff import FigureDiff

class Rule:
    def __init__(self, figure_sequence):
        adjacent_pairs = self._pair_adjacent_elements(figure_sequence)
        self.adjacent_pair_figure_diffs = [FigureDiff(before, after) for before, after in adjacent_pairs]

    def __repr__(self):
        return "<Rule adjacent_pair_figure_diffs : %s>" % (self.adjacent_pair_figure_diffs,)

    def similarity_to(self, other):
        '''
        Score similarity to another Rule, based on figure_diff similarity.
        @return a numeric score from 0 to 1, where 1.0 represents equality
        '''
        similarity_scores = [self.adjacent_pair_figure_diffs[i].similarity_to(other.adjacent_pair_figure_diffs[i]) for i in range(len(self.adjacent_pair_figure_diffs))]
        avg_similarity_score = sum(similarity_scores) / len(similarity_scores)
        return avg_similarity_score

    def _pair_adjacent_elements(self, items):
        if len(items) == 2:
            return ((items[0], items[1]),)
        elif len(items) == 3:
            return ((items[0], items[1]),)
        else:
            raise ValueError("Adjacent pairing unimplemented for list size %d" % (items.size,))
