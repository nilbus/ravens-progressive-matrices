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

from Rule import Rule

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
        print answer_probabilities
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
            raise ValueError('Unimplemented problem type: %s' % self.problem_type)

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
        if len(relationship) == 2:
            return self.possible_binary_transformations(relationship, rule_count_limit)
        else:
            raise ValueError('Relationships of size != 2 are unimplemented')

    def possible_binary_transformations(self, relationship, rule_count_limit=1):
        '''
        @return a list of Rule objects, no longer than rule_count_limit
        '''
        extract_objects = lambda figure: figure.objects
        (before, after) = map(extract_objects, relationship)
        return [Rule(before, after)]

    def guess_probabilities(self, transformation_rules_with_figure_keys):
        '''
        @return an array of positive probabilities that sum to 1.0
        '''
        transformation_rules = self.rekey_figure_keys_as_names(transformation_rules_with_figure_keys)
        rule_group_answer_correlation_scores = \
            [self.rule_group_answer_correlations(rule_group, transformation_rules) \
                    for rule_group in self.problem_type_relationships()]
        answer_relationship_scores = self.combine_rule_group_answer_scores(rule_group_answer_correlation_scores)
        return normalize(answer_relationship_scores)

    def rekey_figure_keys_as_names(self, dict_with_figure_tuple_keys):
        '''
        For each key in the given dict, map the Figure to Figure.name
        '''
        return {tuple(map(lambda figure: figure.name, figures)) : rules \
                for figures, rules in dict_with_figure_tuple_keys.iteritems()}

    def rule_group_answer_correlations(self, rule_group, transformation_rules):
        '''
        @return a list with one entry per rule group, where each entry is a list
        containing correlation scores for each answer.
        '''
        given_sequence_names  = rule_group[0]
        answer_sequence_names = rule_group[1]
        given_sequence_rules  = [transformation_rules[sequence] for sequence in given_sequence_names]
        answer_sequence_rules = [transformation_rules[sequence] for sequence in answer_sequence_names]
        answer_correlations = [self.score_sequence_correlation(given_sequence_rules, answer_sequence_rules) \
                for answer_sequence_rule in answer_sequence_rules]
        return answer_correlations

    def score_sequence_correlation(self, given_rules, proposed_answer_rules):
        '''
        @param given_rules list (of size n ??) of lists of alternate # rules
        @param proposed_answer_rules list (of size n answers) of lists of alternate # rules
        @return a correlation score for the given_sequence_rules with the proposed_answer_rules
        '''
        # TODO: Multiple alternate rules come in, and this always chooses the first. Try different combinations.
        first = lambda x: x[0]
        given_rules           = map(first, given_rules)
        proposed_answer_rules = map(first, proposed_answer_rules)
        alternate_rule_scores = [proposed_answer_rules[alt_n].similarity_to(given_rules[0]) for alt_n in range(len(proposed_answer_rules))]
        return max(alternate_rule_scores)


    def combine_rule_group_answer_scores(self, rule_group_answer_correlations):
        '''
        Add scores from each relationship. It will be common, especially for 3x3
        matrices, to have problems where some relationships have no rule. Adding scores
        will cause those relationships to be ignored.
        @return a list of combined scores for each answer
        '''
        return np.sum(rule_group_answer_correlations, axis=0)

def normalize(list):
    return np.array(list) / sum(list)

def filter_dict(predicate, d):
    return {key:val for key, val in d.iteritems() if predicate(key, val)}

def flatten(l):
    return [item for sublist in l for item in sublist]
