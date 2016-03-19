from copy import copy
import numpy as np

class FigureDiff:
    def __init__(self, before, after):
        self.before = before
        self.after = after
        paired_objects = self._pair_ravens_objects(before.objects(), after.objects())
        self.diff = self._diff(paired_objects)

    def __repr__(self):
        return "<FigureDiff %s>" % (self.diff,)

    def __getitem__(self, key):
        return self.diff[key]

    def get(self, key, default):
        return self.diff.get(key, default)

    def objects(self):
        return self.diff.keys()

    def similarity_to(self, other):
        '''
        Try to match up 'before' objects between the two rules into paired_objects.
        Compare compare those paired_objects' rules.
        @return a numeric score from 0 to 1, where 1.0 represents equality
        '''
        diff_pairs = self._match_diffs(self, other)
        score_multipliers = [self._diff_similarity(diff_pair) for diff_pair in diff_pairs]
        overall_score = reduce(lambda a, e: a * e, score_multipliers, 1.0)
        return overall_score

    def _match_diffs(self, diff_a, diff_b):
        '''
        @param diff_a : a diff between two frames
        @param diff_a : a second diff to compare with diff_a
        @return a numeric score from 0 to 1, where 1.0 represents equality
        '''
        diff_a = copy(diff_a)
        diff_b = copy(diff_b)
        matching_objects = self._pair_ravens_objects(diff_a.objects(), diff_b.objects())
        matching_diffs = map(lambda pair: (diff_a.get(pair[0], NoMatch), diff_b.get(pair[1], NoMatch)), matching_objects)
        return matching_diffs

    def _diff_similarity(self, diff_pair):
        score = 1.0
        (diff_a, diff_b) = diff_pair
        diff_b = copy(diff_b)
        score *= self._discount_diff_additions_removals(diff_a, diff_b)
        score *= self._discount_differing_changes(diff_a, diff_b)
        return score

    def _discount_diff_additions_removals(self, diff_a, diff_b):
        extra_or_missing_object_discount = 0.6
        additions_removals_a = diff_a.added() | diff_a.removed()
        additions_removals_b = diff_b.added() | diff_b.removed()
        non_common_additions_removals = additions_removals_a ^ additions_removals_b
        multiplier = extra_or_missing_object_discount ** len(non_common_additions_removals)
        return multiplier

    def _discount_differing_changes(self, diff_a, diff_b):
        differing_change_discount = 0.6
        changed_keys_a = diff_a.changed()
        changed_keys_b = diff_b.changed()
        changes_a = {key: diff_a.before[key] for key in changed_keys_a}
        changes_b = {key: diff_b.before[key] for key in changed_keys_b}
        change_comparison = DictDiffer(changes_a, changes_b)
        differing_change_keys = change_comparison.added() | change_comparison.removed() | change_comparison.changed()
        # TODO: account for rotation, flipping, symmetry, alignment shifts, etc
        multiplier = differing_change_discount ** len(differing_change_keys)
        return multiplier

    def _pair_ravens_objects(self, set_a, set_b):
        '''
        Go through the smallest set of objects, and pair each with best matches from the
        other set. If the other set is larger, its worst-matching objects will remain
        unpaired.
        @return a list of pair tuples, with a NoObject instance replacing any nonexistent object
        '''
        pairs = []
        smaller_set = set_a if len(set_a) <= len(set_b) else set_b
        larger_set  = set_a if len(set_a) >  len(set_b) else set_b
        # FIXME: Pairing is not always happening right. The best matches in
        # larger_set are being snatched up by earlier elements in smaller_set when
        # there is no great match.
        for left_obj in smaller_set:
            similarities = np.array([self._obj_similarity(left_obj, right_obj) for right_obj in larger_set])
            most_similar_index = similarities.argmax()
            most_similar = larger_set.pop(most_similar_index)
            pairs.append((left_obj, most_similar))
        for right_obj in larger_set:
            pairs.append((NoObject, right_obj))
        if smaller_set == set_b:
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

    def _diff(self, paired_objects):
        '''
        @return a dict of source RavensObject instances to DictDiffer instances
        '''
        diff = {}
        for paired_object in paired_objects:
            (before, after) = paired_object
            diff[before] = DictDiffer(before.attributes, after.attributes)
        return diff

class _NoObject:
    def __init__(self):
        self.name = None
        self.attributes = {}

NoObject = _NoObject()

# DictDiffer adapted from hughdbrown's post at http://stackoverflow.com/a/1165552/87298
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
    def __repr__(self):
        return "<DictDiffer before: %s, after: %s, added: %s; removed: %s, changed: %s>" % \
                (self.before, self.after, self.added(), self.removed(), self.changed())
    def __len__(self):
        return sum((len(self.added()), len(self.removed()), len(self.changed())))

NoMatch = DictDiffer({}, {'no_matching_object': True})
