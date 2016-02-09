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

# Install Numpy and uncomment this line to access matrix operations.
import numpy as np

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
        figures = problem.figures
        problem_relationships = self.problem_type_relationships(problem.problemType)
        related_figures = self.group_related_figures(figures, problem_relationships)
        transformation_rules = self.detect_rules(related_figures)
        answer_probabilities = self.guess_probabilities(transformation_rules)
        return answer_probabilities

    def problem_type_relationships(self, problem_type):
        if problem_type == '2x2':
            return (
                ('A', 'B'), ('A', 'C'),
                ('B', '1'), ('C', '1'),
                ('B', '2'), ('C', '2'),
                ('B', '3'), ('C', '3')
            )
        else:
            raise ValueError('Unimplemented problem type: %s' % problem_type)

    # Map figure names to Figure objects
    # @return ((Figure1, Figure2), (Figure1, Figure3), ...)
    def group_related_figures(self, figures, problem_relationships):
        pass

    # @return a dictionary of (Figure1, Figure2) => [Rule, ...]
    def detect_rules(self, related_figures, rule_count_limit=1):
        pass

    # @return an array of positive probabilities that sum to 1.0
    def guess_probabilities(self, transformation_rules):
        pass

