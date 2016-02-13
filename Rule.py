from copy import copy
import numpy as np

# For 2x2, a tranformation
class Rule:
    def __init__(self, before, after):
        self.before = before
        self.after = after
        self.pairs = self._pair_objects(before, after)
        self.diff = self._diff(self.pairs)

    def similarity_to(self, other):
        '''
        @return a numeric score from 0-1, where 1.0 represents equality
        '''
        return 1.0

    def _pair_objects(self, set_a, set_b):
        '''
        Go through the smallest set of objects, and pair each with best matches from the
        other set. If the other set is larger, its worst-matching objects will remain
        unpaired.
        @return a list of pair tuples, with a NoObject instance replacing any nonexistent object
        '''
        pairs = []
        smaller_set = set_a.values() if len(set_a) <= len(set_b) else set_b.values()
        larger_set  = set_a.values() if len(set_a) >  len(set_b) else set_b.values()
        # FIXME: Pairing is not always happening right. The best matches in
        # larger_set are being snatched up by earlier elements in smaller_set when
        # there is no great match.
        for left_obj in smaller_set:
            similarities = np.array([self._obj_similarity(left_obj, right_obj) for right_obj in larger_set])
            most_similar_index = similarities.argmax()
            most_similar = larger_set.pop(most_similar_index)
            pairs.append((left_obj, most_similar))
        for right_obj in larger_set:
            pairs.append((NoObject(), right_obj))
        if smaller_set == set_b.values():
            reverse = lambda pair: tuple(reversed(pair))
            pairs = map(reverse, pairs)
        # for pair in pairs:
        #     print map(lambda object: object.attributes, pair)
        # print
        return pairs

    def _obj_similarity(self, obj_a, obj_b):
        attr_a, attr_b = obj_a.attributes, copy(obj_b.attributes)
        score = 0
        for attr, value in attr_a.iteritems():
            if attr == 'shape':
                weight = 10
            elif attr == 'size':
                weight = 8
            else:
                weight = 6
            if attr in attr_b:
                if value == attr_b[attr]:
                    score += weight
                else:
                    score -= weight
                del attr_b[attr]
            else:
                score -= 4
        score -= 4 * len(attr_b)
        return score

    def _diff(self, pairs):
        '''
        @return a dict of source RavensObject instances to DictDiffer instances
        '''
        diff = {}
        for pair in pairs:
            (before, after) = pair
            diff[before] = DictDiffer(before.attributes, after.attributes)
        return diff

class NoObject:
    def __init__(self):
        self.name = None
        self.attributes = {}

# DictDiffer source: hughdbrown, from http://stackoverflow.com/a/1165552/87298
# Copied with some modifications.
class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, before, after):
        self.after, self.before = after, before
        self.set_current, self.set_past = set(after.keys()), set(before.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.before[o] != self.after[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.before[o] == self.after[o])
