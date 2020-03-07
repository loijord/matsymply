from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import sympy as sp #pprint, latex, Rational
transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
import itertools
import random

class Quiz:
    def __init__(self, problems=[], answers=[], size=10):
        self.problems = problems
        self.answers = answers
        self.gen = iter(range(size))

    def next(self):
        id = next(self.gen)
        return self.problems[id], self.answers[id]

    def add(self, problem, answer):
        self.problems.append(problem)
        self.answers.append(answer)

    def flip(self):
        self.answers, self.problems = self.problems, self.answers


class Creator:
    domain = itertools.chain(range(-9, 0), range(1, 10))
    def __init__(self, type, size):
        self.quiz = Quiz()
        self.type = type
        self.size = size

        if type == 1:
            self.create_quiz("(x+a)(x+b)", lambda X: sp.expand(X))
        if type == 2:
            self.create_quiz("(x+a)(x-a)", lambda X: sp.expand(X))
        if type == 3:
            self.create_quiz("(x+a)(x+a)", lambda X: sp.expand(X))
        if type == 4:
            self.create_quiz("(x+a)(x+b)", lambda X: sp.expand(X), reverse=True)
        if type == 5:
            self.create_quiz("(x+a)(x-a)", lambda X: sp.expand(X), reverse=True)
        if type == 6:
            self.create_quiz("(x+a)(x+a)", lambda X: sp.expand(X), reverse=True)

    def get_quiz(self):
        return self.quiz

    def create_quiz(self, formula, call, reverse=False):
        free_variables = sorted(set(n for n in formula if n in 'abcdefghijkl'))
        choice = list(itertools.permutations(self.domain, len(free_variables)))
        e = parse_expr(formula, transformations=transformations)
        for n in random.sample(choice, self.size):
            problem_expr = e.subs(dict(zip(free_variables, n)))
            answer_expr = call(problem_expr)
            # print(sp.latex(problem_expr))
            # print(sp.latex(answer_expr))
            self.quiz.add(problem_expr, answer_expr)
        if reverse: self.quiz.flip()