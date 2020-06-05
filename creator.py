from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import sympy as sp #pprint, latex, Rational
transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
import itertools
import random
from functools import reduce

class Specialform:
    # union of 3 forms of expresion: text, sympy and latex
    def __init__(self):
        self.state = 0
        self.sympy = None
        self.latex = None
        self.symform1 = Symform('')
        self.symform2 = Symform('')
        self.steps = None

    def add(self, step):
        if self.state == 1:
            self.symform1.add(step)
            #self.plain = r"\frac{{{}}}{{\\cdot}}".format(self.symform1.get_plain())
            #self.steps.append(self.plain)
        elif self.state == 2:
            self.symform2.add(step)
            #self.plain = r"\frac{{{}}}{{{}}}".format(self.symform1.get_plain(), self.symform1.get_plain())
            #self.steps.append(self.plain)

    def rewind(self):
        if self.plain != '':
            self.plain = self.plain[:-len(self.steps[-1])]
            del self.steps[-1]

    def tosympy(self):
        if self.state == 0:
            self.symform1.tosympy()
            self.symform2.tosympy()
            self.sympy = self.symform1.get_sympy() / self.symform2.get_sympy()

class Symform:
    #union of 3 forms of expresion: text, sympy and latex
    def __init__(self, anyform):
        self.sympy = None
        self.latex = None
        self.plain = None
        self.steps = []
        # expected states: fraction, pow, sqrt
        if isinstance(anyform, tuple(sp.core.all_classes)):
            self.sympy = anyform
        elif isinstance(anyform, str):
            if '$' in anyform:
                self.latex = anyform
            else:
                self.plain = anyform
        else:
            raise TypeError(f'Expression {anyform} is expected to be of plain, latex or sympy type')

    def add(self, step):
        self.steps.append(step)
        self.plain += step

    def rewind(self):
        if self.plain != '':
            self.plain = self.plain[:-len(self.steps[-1])]
            del self.steps[-1]

    def __repr__(self):
        forms = {'plain': self.plain, 'latex':self.latex, 'sympy':self.sympy}
        representations = [f'\t{n}: {forms[n]}' for n in forms if forms[n] is not None]
        return f'symform that contains:\n' + ''.join(representations)

    def get_plain(self):
        return self.plain

    def get_sympy(self):
        return self.sympy

    def get_latex(self):
        return self.latex

    def tosympy(self): #uses plain text
        if self.plain != '' and self.sympy is None:
            with sp.evaluate(False):
                self.sympy = parse_all(self.get_plain(), transformations=transformations)

    def tolatex(self, compile = True):
        # try to parse and extract latex from parsed expression (if compile is True)
        # if not successful, convert plain to latex (or if compile is False)

        if self.plain != '':
            try:
                if compile is False: raise TypeError
                if self.sympy is None:
                    self.tosympy()
                self.latex = '$'+sp.latex(self.sympy)+'$'
            except Exception as e:
                self.latex = '$'+sp.latex(self.plain)+'$'
        else:
            self.latex = ''


class Question:
    def __init__(self, problem, answer):
        self.problem = problem
        self.answer = answer

    def flip(self):
        self.answer, self.problem = self.problem, self.answer


class Quiz:
    def __init__(self, questions=[], size=10):
        self.questions = questions
        self.gen = iter(range(size))

    def next(self):
        id = next(self.gen)
        return self.questions[id]

    def add(self, question):
        self.questions.append(question)

    def flip(self):
        for question in self.questions:
            question.flip()

class Creator:
    domain = list(itertools.chain(range(-9, 0), range(1, 10)))
    def __init__(self, type, size):
        self.quiz = Quiz(questions=[], size=size)
        self.type = type
        self.size = size

        if type == 1:
            self.create_quiz("(x+a)(x+b)", lambda X: sp.expand(X), filt=lambda a,b: a!=b)
        if type == 2:
            self.create_quiz("(x+a)(x-a)", lambda X: sp.expand(X))
        if type == 3:
            self.create_quiz("(x+a)(x+a)", lambda X: sp.expand(X))
        if type == 4:
            self.create_quiz("(x+a)(x+b)", lambda X: sp.expand(X), reverse=True, filt=lambda a,b: a!=b)
        if type == 5:
            self.create_quiz("(x+a)(x-a)", lambda X: sp.expand(X), reverse=True)
        if type == 6:
            self.create_quiz("(x+a)(x+a)", lambda X: sp.expand(X), reverse=True)
        if type == 7:
            self.create_quiz(("a(bx+c)","a(c+bx)"), lambda X: sp.expand(X), reverse=False, evaluate=False,
                             domain=[list(itertools.chain(range(-9, 0), range(2, 10))), self.domain, self.domain])
        if type == 8:
            self.create_quiz(("ax(bx+c)","ax(c+bx)"), lambda X: sp.expand(X), reverse=False)
        if type == 9:
            self.create_quiz("(ax+b)-(cx+d)", lambda X: sp.expand(X), reverse=False, evaluate=True,
                             domain=[[1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9]])
        if type == 10:
            self.create_quiz("ax*bx+d*(e+fx)", lambda X: sp.expand(X), reverse=False)
        if type == 11:
            self.create_quiz("a(bx+c)", lambda X: sp.expand(X), reverse=True)
        if type == 12:
            self.create_quiz("ax(bx+c)", lambda X: sp.expand(X), reverse=True)

        if type == 13:
            x = sp.Symbol('x')
            self.create_quiz(("ax=b", "b=ax"), lambda X: sp.Eq(x, sp.solve(X)[0]), reverse=False,
                             domain=[[2,3,4,5,6,7,8,9,-1,-2,-3,-4,-5,-6,-7,-8,-9],
                                     [4,6,8,9,10,12,14,16,18,15,20,21,28,27,24,30,32,36,40,35,42,
                                      -4,-6,-8,-9,-10,-12,-14,-16,-18,-15,-20,-21,-28,-27,-24,-30,-32,-36,-40,-35,-42]],
                             filt=lambda a,b: (b/a==b//a))
        if type == 14:
            x = sp.Symbol('x')
            self.create_quiz(("ax=b", "b=ax"), lambda X: sp.Eq(x, sp.solve(X)[0]), reverse=False,
                             domain=[[2, 3, 4, 5, 6, 7, 8, 9, -1, -2, -3, -4, -5, -6, -7, -8, -9],
                                     [4, 6, 8, 9, 10, 12, 14, 16, 18, 15, 20, 21, 28, 27, 24, 30, 32, 36, 40, 35, 42,
                                      -4, -6, -8, -9, -10, -12, -14, -16, -18, -15, -20, -21, -28, -27, -24, -30, -32,
                                      -36, -40, -35, -42]])
        if type == 15:
            x = sp.Symbol('x')
            self.create_quiz(("a+x=b", "x+a=b", "b=x+a", "b=a+x"), lambda X: sp.Eq(x, sp.solve(X)[0]), reverse=False)
        if type == 16:
            x = sp.Symbol('x')
            self.create_quiz(("ax=b+cx", "b+cx=ax"), lambda X: sp.Eq(x, sp.solve(X)[0]), reverse=False,
                             filt=lambda a,b,c: (a!=c) and (b/(a-c)==b//(a-c)))
        if type == 17:
            x = sp.Symbol('x')
            self.create_quiz("ax+b=cx+d", lambda X: sp.Eq(x, sp.solve(X)[0]), reverse=False,
                             filt=lambda a,b,c,d: (a!=c) and ((d-b)/(a-c) == (d-b)//(a-c)))
        if type == 18:
            x = sp.Symbol('x')
            self.create_quiz("ax+b=cx+d", lambda X: sp.Eq(x, sp.solve(X)[0]), reverse=False,
                             filt=lambda a,b,c,d: a!=c)

    def get_quiz(self):
        return self.quiz

    def create_quiz(self, formula, call, reverse=False, filt=None, domain=None, evaluate=True):
        # expects to parse expression from string and calculate:
        # problem_expr as sympy object (expr or eq)
        # answer_expr as sympy object of the same type

        #formula can be either string or tuple of strings
        if isinstance(formula, str): f = formula
        else: f = reduce(lambda x,y: x+y, formula)

        free_variables = sorted(set(n for n in f if n in 'abcdefghijkl'))
        if domain is None:
            domain = [self.domain for n in range(len(free_variables))]
        #else: expected to be list of lists
        choice = list(itertools.product(*domain))
        if filt is not None:
            choice = list(filter(lambda x: filt(*x), choice))

        if isinstance(formula, str):
            e = [parse_all(formula, transformations=transformations)]
        else:
            e = [parse_all(f, transformations=transformations) for f in formula]
        for n in random.sample(choice, self.size):
            N = random.randint(0, len(e)-1)
            if not(evaluate):
                with sp.evaluate(False):
                    problem_expr = e[N].subs(dict(zip(free_variables, n)))
            else:
                problem_expr = e[N].subs(dict(zip(free_variables, n)))
            answer_expr = call(problem_expr)
            # print(sp.latex(problem_expr))
            # print(sp.latex(answer_expr))
            self.quiz.add(Question(problem_expr, answer_expr))
        if reverse: self.quiz.flip()


def parse_all(formula, transformations=transformations):
    if '=' not in formula:
        return parse_expr(formula, transformations=transformations)
    else:
        LHS, RHS = formula.split('=')
        lhs_e = parse_expr(LHS, transformations=transformations)
        rhs_e = parse_expr(RHS, transformations=transformations)
    return sp.Eq(lhs_e, rhs_e)


