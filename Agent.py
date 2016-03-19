# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
#from PIL import Image
import numpy as np
import re

from FigureObjectSet import FigureObjectSet
from Rule import Rule

import Debug
import pdb

class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return a list representing its
    # confidence on each of the answers to the question: for example
    # [.1,.1,.1,.1,.5,.1] for 6 answer problems or [.3,.2,.1,.1,0,0,.2,.1] for 8 answer problems.
    #
    # In addition to returning your answer at the end of the method, your Agent
    # may also call problem.checkAnswer(givenAnswer). The parameter
    # passed to checkAnswer should be your Agent's current guess for the
    # problem; checkAnswer will return the correct answer to the problem. This
    # allows your Agent to check its answer. Note, however, that after your
    # agent has called checkAnswer, it will *not* be able to change its answer.
    # checkAnswer is used to allow your Agent to learn from its incorrect
    # answers; however, your Agent cannot change the answer to a question it
    # has already answered.
    #
    # If your Agent calls checkAnswer during execution of Solve, the answer it
    # returns will be ignored; otherwise, the answer returned at the end of
    # Solve will be taken as your Agent's answer to this problem.
    #
    # Make sure to return your answer *as a python list* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self, problem):
        self.problem_type = problem.problemType
        if not problem.hasVerbal: # So far, no image processing implemented
            return np.ones(6 if self.problem_type == '2x2' else 8)
        figures = problem.figures
        problem_relationships = flatten(flatten(self.problem_type_relationships()))
        related_figures = self.collect_related_figures(figures, problem_relationships)
        transformation_rules = self.detect_rules(related_figures)
        answer_probabilities = self.guess_probabilities(transformation_rules)
        return answer_probabilities

    def problem_type_relationships(self):
        '''
        Each inner tuple represents a set of figures that represent some relationship.
        These are organized into groups of Given and Potential Answer sets.
        Each group of Given + Potential Answer relationships potentially share common
        rules, along which we'll call a rule group.
        Summary of the 3 layers:
        1. Rule group: items share rules
        2. 2 items contain Given and Potential Answers, respectively
        3. Figure names are part of a sequence
        '''
        if self.problem_type == '2x2':
            return (
                (
                    (('A', 'B'),),
                    (('C', '1'), ('C', '2'), ('C', '3'), ('C', '4'), ('C', '5'), ('C', '6'))
                ), (
                    (('A', 'C'),),
                    (('B', '1'), ('B', '2'), ('B', '3'), ('B', '4'), ('B', '5'), ('B', '6'))
                )
            )
        else:
            return (
                (
                    (('A','B','C'),('D','E','F')),
                    (('G','H','1'),('G','H','2'),('G','H','3'),('G','H','4'),('G','H','5'),('G','H','6'))
                ), (
                    (('A','D','G'),('B','E','H')),
                    (('C','F','1'),('C','F','2'),('C','F','3'),('C','F','4'),('C','F','5'),('C','F','6'))
                )
            )

    def collect_related_figures(self, figures, problem_relationships):
        '''
        Map figure names to Figure objects
        @return ((Figure1, Figure2), (Figure1, Figure3), ...)
        '''
        relationship_mapper = lambda relationship: \
                tuple([figures[relationship[i]] for i in (range(len(relationship)))])
        return map(relationship_mapper, problem_relationships)

    def detect_rules(self, related_figures, rule_count_limit=1):
        '''
        @return a dictionary of (Figure1, Figure2) => [Rule, ...]
        '''
        self.curret_rule_count_limit = rule_count_limit
        rule_mapper = lambda relationship: \
                self.detect_relationship_rules(relationship, rule_count_limit)
        relationships_rules = map(rule_mapper, related_figures)
        return dict(zip(related_figures, relationships_rules))

    def detect_relationship_rules(self, relationship, rule_count_limit=1):
        '''
        @return a list of Rule objects, no longer than rule_count_limit
        '''
        extract_objects = lambda figure: FigureObjectSet(figure.objects)
        figure_sequence = map(extract_objects, relationship)
        return [Rule(figure_sequence)]

    def guess_probabilities(self, transformation_rules_with_figure_keys):
        '''
        @return an array of positive probabilities that sum to 1.0
        '''
        transformation_rules = self.rekey_figure_keys_as_names(transformation_rules_with_figure_keys)
        rule_group_answer_correlation_scores = \
            [self.rule_group_answer_correlations(rule_group, transformation_rules) \
                    for rule_group in self.problem_type_relationships()]
        answer_relationship_scores = self.combine_rule_group_answer_scores(rule_group_answer_correlation_scores)
        return normalize(self.boost(answer_relationship_scores))

    def rekey_figure_keys_as_names(self, dict_with_figure_tuple_keys):
        '''
        For each key in the given dict, map the Figure to Figure.name
        '''
        return {tuple(map(lambda figure: figure.name, figures)) : rules \
                for figures, rules in dict_with_figure_tuple_keys.iteritems()}

    def rule_group_answer_correlations(self, rule_group, transformation_rules):
        '''
        @param rule_group triply nested tuples in the same structure as documented in
            self.problem_type_relationships().
        @return a list with one entry per rule group, where each entry is a list
        containing correlation scores for each answer.
        '''
        given_sequence_names  = rule_group[0]
        answer_sequence_names = rule_group[1]
        given_sequence_rules  = [transformation_rules[sequence] for sequence in given_sequence_names]
        answer_sequence_rules = [transformation_rules[sequence] for sequence in answer_sequence_names]
        answer_correlations = \
                [self.score_sequence_correlation(given_sequence_rules, answer_sequence_rule_alts) \
                 for answer_sequence_rule_alts in answer_sequence_rules]
        return answer_correlations

    def score_sequence_correlation(self, given_rules, proposed_answer_rule_alts):
        '''
        @param given_rules list (of size n givens in the sequence [1 for a 2x2]]) of lists of alternate rules
        @param proposed_answer_rule_alts a list of alternate rules for the proposed answer under test
        @return a correlation score for each answer in the proposed_answer_rules with the given_sequence_rules
        '''
        # TODO: Multiple alternate rules come in for the given list, and this always chooses the first. Try different combinations.
        first = lambda x: x[0]
        given_rules = map(first, given_rules)
        rule_alternate_scores = [proposed_answer_rule_alts[alt_n].similarity_to(given_rules[0]) for alt_n in range(len(proposed_answer_rule_alts))]
        return max(rule_alternate_scores)

    def combine_rule_group_answer_scores(self, rule_group_answer_correlations):
        '''
        Add scores from each relationship. It will be common, especially for 3x3
        matrices, to have problems where some relationships have no rule. Adding scores
        will cause those relationships to be ignored.
        @return a list of combined scores for each answer
        '''
        return np.sum(rule_group_answer_correlations, axis=0)

    def boost(self, scores):
        method = 'max'
        scores = np.array(scores)
        if method == 'none':
            result = scores
        elif method == 'square':
            result = scores ** 2
        elif method == 'cube':
            result = scores ** 3
        elif method == 'max':
            max_value = scores.max()
            result = np.where(scores == max_value, np.ones(scores.shape), np.zeros(scores.shape)).flatten()
        else:
            raise ValueError('no valid boost method selected')
        return tuple(result)

def normalize(list):
    return np.array(list) / sum(list)

def filter_dict(predicate, d):
    return {key:val for key, val in d.iteritems() if predicate(key, val)}

def flatten(l):
    return [item for sublist in l for item in sublist]
