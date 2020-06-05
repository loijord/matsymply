tasks = [13, 14, 15, 16, 17, 18]
#tasks = [1, 2, 3, 4, 5, 6]

from creator import Creator, Symform, Specialform
from database import write, read
from tkinter import Button, Tk, font, Label, Frame
from PIL import Image, ImageTk
from matplotlib import use
import sys
sys.setrecursionlimit(100000)
use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import time
from datetime import datetime

from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import sympy as sp #pprint, latex, Rational
transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
import json

#from matplotlib.figure import Figure

"""class ThrowNumbers:
    def __init__(self, possibles, size, type='distinct'):
        if type == 'distinct':
            self.out = random.sample(list(itertools.permutations(possibles, size)))
        if type == 'any':
            self.out = random.choice(list(itertools.product(possibles, repeat=size)))"""

class Timer:
    def __init__(self, master):
        self.master = master
        self.time = time.time()
        self.field = Label(master, text='0', width=3,
                           fg="#{0:02x}{1:02x}{2:02x}".format(255, 255, 255),
                           font=font.Font(family='Helvetica', weight='bold', size=20),
                           bg="#{0:02x}{1:02x}{2:02x}".format(32, 80, 96),
                           borderwidth=5, relief="groove", anchor="e")
        self.field.grid(row=1, column=5, rowspan=2)
        self.update()

    def update(self):
        now = round(time.time() - self.time)
        self.field.configure(text=now)
        self.master.after(1000, self.update)

    def reset(self):
        self.time = time.time()

class Starpacket:
    def __init__(self, master):
        self.master = master
        self.labels = []
        self.emptystar_image = Image.open(r'images\emptystar.png').resize((30, 30), Image.ANTIALIAS)
        self.fullstar_image = Image.open(r'images\fullstar.png').resize((30, 30), Image.ANTIALIAS)
        self.emptystar_photo = ImageTk.PhotoImage(self.emptystar_image)
        self.fullstar_photo = ImageTk.PhotoImage(self.fullstar_image)
        self.field = Frame(master)
        self.field.grid(row=0, column=0, columnspan=5, sticky='W')

    def credit(self, correctness):
        if correctness:
            self.labels.append(Label(self.field, image=self.fullstar_photo))
        else:
            self.labels.append(Label(self.field, image=self.emptystar_photo))
        self.labels[-1].pack(side="left")

    def remove(self):
        for n in self.labels:
            n.pack_forget()


class Response:
    def __init__(self, master, image_name):
        self.image = ImageTk.PhotoImage(Image.open(image_name).resize((70, 70), Image.ANTIALIAS))
        self.photo = Label(master, image=self.image)
        self.photo.image = self.image
        self.field = Label(master, image=self.image)

class Problem:
    def __init__(self, master, symform):
        #shoul be initialized from expression[not possible] or text form[used]
        print('symform = ', symform)
        self.master = master
        self.field = Label(master, width=15,
                                   fg="#{0:02x}{1:02x}{2:02x}".format(255, 255, 255),
                                   font=font.Font(family='Helvetica', weight='bold', size=20),
                                   bg="#{0:02x}{1:02x}{2:02x}".format(128, 128, 96),
                                   borderwidth=5, relief="raised")
        self.field.grid(row=1, column=1, columnspan=4, sticky="nesw")
        self.update(symform)

    def update(self, symform): #r'x\sqrt{\frac{3}{4}}'
        fig = plt.figure(figsize=(7, 1), dpi=50, facecolor='yellow')
        ax = fig.gca()
        ax.clear()
        symform.tolatex()
        ax.text(0.0, 0.0, symform.get_latex(), fontsize=40), #bbox=dict(facecolor='red', alpha=0.5))
        ax.axis('off')
        # for item in [ax, fig]: item.patch.set_visible(False)
        ax.get_xaxis().set_visible(True)
        ax.get_yaxis().set_visible(True)

        canvas = FigureCanvasTkAgg(fig, master=self.field)
        canvas_widget = canvas.get_tk_widget()
        #canvas_widget.configure(background='red', highlightcolor='green', highlightbackground='blue')
        canvas_widget.grid(row=1, column=1, columnspan=4, sticky="nesw")
        fig.tight_layout(pad=1)
        canvas.draw()

class Answer:
    def __init__(self, master):
        self.master = master
        self.field = Label(master, activebackground='red',
                                  fg="#{0:02x}{1:02x}{2:02x}".format(0, 64, 0),
                                  bg="#{0:02x}{1:02x}{2:02x}".format(64, 160, 224),
                                  borderwidth=5, relief="ridge")
        # "flat", "raised", "sunken", "ridge", "solid", and "groove"
        self.field.grid(row=2, column=1, columnspan=4, sticky="nesw")
        self.fig = None
        self.ax = None
        self.canvas = None

    def update(self, symform, compile=False):
        #not parses text, displays latex form as it is
        fig = plt.figure(figsize=(7, 1), dpi=50)
        ax = fig.gca()
        symform.tolatex(compile=compile)
        print('updating symform:', symform.get_latex())
        self.txt = ax.text(0.0, 0.0, symform.get_latex(), fontsize=40)#, bbox=dict(facecolor='red', alpha=0.5))
        ax.axis('off')

        self.canvas = FigureCanvasTkAgg(fig, master=self.field)
        canvas_widget = self.canvas.get_tk_widget()
        #canvas_widget.configure(background='red', highlightcolor='green', highlightbackground='blue')
        canvas_widget.grid(row=2, column=1, columnspan=4, sticky="nesw")
        try:
            fig.tight_layout(pad=1)
        except ValueError:
            raise ValueError
        else:
            self.fig, self.ax = fig, ax
            self.canvas.draw()


    def check(self, is_good, symform=None):
        #if is_good = False, correct must be specified
        if is_good:
            self.fig.patch.set_facecolor('#E000E0')
            self.canvas.draw()
        else:
            #self.fig.patch.set_facecolor('#E00000')
            textbox = self.ax.texts[0].get_window_extent()
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(-1, 1)
            self.ax.plot([0, textbox.width / textbox.height / 7], [0, 1], linewidth=3, color = 'red')
            symform.tolatex()
            self.ax.text(0.0, -1.5, symform.get_latex(), fontsize=40)
            self.canvas.draw()


class Key:
    def __init__(self, master, text, color, command, **kwargs):
        self.master = master
        self.state = 'active' #at first its active cuz problem is being solved
        self.button = Button(master, text=text,
                             command=lambda x=text: command(x),
                             bg="#{0:02x}{1:02x}{2:02x}".format(*color), **kwargs)
        self.button.grid(row=4, column=1)  # columnspan=2)

class Calc:
    map = {'Kvadratiniai reiškiniai':[1,2,3,4,5,6], 'Tiesinės lygtys': [13,14,15,16,17,18]}
    def __init__(self, master):
        #if 'register.txt' in os.listdir():
        global tasks
        self.tasks = tasks
        self.compile = False  # situation changes when a new fraction was inputted
        self.master = master
        self.master.title('Calculator')
        self.master.geometry()
        self.level = None
        self.starpacket = Starpacket(master)
        self.specialform = Specialform()
        self.finals_image1 = Image.open(r'images\finals1.png').resize((80, 100), Image.ANTIALIAS)
        self.finals_image2 = Image.open(r'images\finals2.png').resize((80, 100), Image.ANTIALIAS)
        self.finals_image3 = Image.open(r'images\finals3.png').resize((80, 100), Image.ANTIALIAS)
        self.unclear = Response(master, r'images\unclear.png')
        self.winner = Response(master, r'images\winner.png')
        self.loser = Response(master, r'images\loser.png')
        self.finals_field = None

        self.start_game()

        kwargs = {'width': 5, 'activebackground': 'red', 'fg': 'white',
                  'font': font.Font(family='Helvetica', weight='bold', size=20)}

        button7 = Key(master, text='7', color=(96,151,112), command=self.react, **kwargs); button7.button.grid(row=4, column=1)
        button8 = Key(master, text='8', color=(96,151,112), command=self.react, **kwargs); button8.button.grid(row=4, column=2)
        button9 = Key(master, text='9', color=(96,151,112), command=self.react, **kwargs); button9.button.grid(row=4, column=3)
        button4 = Key(master, text='4', color=(80,135,96), command=self.react, **kwargs); button4.button.grid(row=5, column=1)
        button5 = Key(master, text='5', color=(80,135,96), command=self.react, **kwargs); button5.button.grid(row=5, column=2)
        button6 = Key(master, text='6', color=(80,135,96), command=self.react, **kwargs); button6.button.grid(row=5, column=3)
        button1 = Key(master, text='1', color=(64,119,80), command=self.react, **kwargs); button1.button.grid(row=6, column=1)
        button2 = Key(master, text='2', color=(64,119,80), command=self.react, **kwargs); button2.button.grid(row=6, column=2)
        button3 = Key(master, text='3', color=(64,119,80), command=self.react, **kwargs); button3.button.grid(row=6, column=3)
        button0 = Key(master, text='0', color=(48,87,64), command=self.react, **kwargs); button0.button.grid(row=7, column=1)  # columnspan=2)

        #this time self.react(x, master=master) unpacks differently
        buttonOK = Key(master, text='OK', color=(48, 87, 64), command=self.react, **kwargs);
        buttonOK.button.config(width=10)
        buttonOK.button.grid(row=7, column=2, columnspan=2)

        kwargs = {'width': 3, 'activebackground': 'blue', 'fg': 'blue',
                  'font': font.Font(family='Helvetica', weight='bold', size=20), 'padx':8}  # size=5

        buttonleft = Key(master, text='(', color=(98, 187, 64), command=self.react, **kwargs)
        buttonleft.button.grid(row=4, column=4)
        buttonright = Key(master, text=')', color=(98, 187, 64), command=self.react, **kwargs)
        buttonright.button.grid(row=4, column=5)

        buttonsq = Key(master, text='²', color=(98, 187, 64), command=self.react, **kwargs)
        buttonsq.button.grid(row=5, column=4)
        kwargs['fg'] = 'black'
        buttonback = Key(master, text='back', color=(98, 187, 64), command=self.react, **kwargs)
        buttonback.button.grid(row=5, column=5)
        kwargs['fg'] = 'blue'
        buttonplus = Key(master, text='+', color=(198, 187, 64), command=self.react, **kwargs)
        buttonplus.button.grid(row=6, column=4)
        buttonminus = Key(master, text='-', color=(198, 187, 64), command=self.react, **kwargs)
        buttonminus.button.grid(row=6, column=5)
        buttontimes = Key(master, text='*', color=(198, 187, 64), command=self.react, **kwargs)
        buttontimes.button.grid(row=7, column=4)
        kwargs['fg'] = 'black'
        buttonx = Key(master, text='x', color=(198, 187, 64), command=self.react, **kwargs)
        buttonx.button.grid(row=7, column=5)

        #"flat", "raised", "sunken", "ridge", "solid", and "groove"
        buttonequal = Key(master, text='=', color=(127, 127, 0), command=self.react, **kwargs, relief='raised',borderwidth=3)
        buttonequal.button.grid(row=4, column=6)
        self.superbutton = Key(master, text='·/·', color=(0, 127, 127), command=self.react, **kwargs, relief='raised',
                          borderwidth=3)
        self.superbutton.button.grid(row=5, column=6)
        """buttondot = Key(master, text='/', color=(127, 0, 127), command=self.react, **kwargs, relief='raised',
                          borderwidth=3)
        buttondot.button.grid(row=6, column=6)
        buttonq = Key(master, text='?', color=(198, 0, 0), command=self.react, **kwargs, relief='raised',
                          borderwidth=3)
        buttonq.button.grid(row=7, column=6)"""
        self.master.grid_rowconfigure(0, minsize=40)
        self.master.grid_rowconfigure(2, minsize=60)

    def update_quiz(self, type, size=10):
        creator = Creator(type, size)
        self.quiz = creator.get_quiz()
        """
        if type == 3:
            x, = ThrowNumbers(itertools.chain(range(-9, 0), range(1, 10)), 1).out
            #self.problem = Expr(f'x²-[frac({x},{x})]').format()
            self.problemstr = Expr(f'x²-[{x * x}]').format()
            self.answerstr = (Expr(f'(x+[{x}])(x-[{x}])').format(),
                           Expr(f'(x-[{x}])(x+[{x}])').format())

        if type == 4:
            x,y,z = ThrowNumbers(itertools.chain(range(-9, 0), range(1, 10)), 3).out
            self.problemstr = Expr(f'[{x}]x([{y}]x+[{z}])').format(),
            self.answerstr = (Expr(f'[{x*y}]x²+[{x*z}]x)').format(),)

        if type == 5:
            t=random.randint(1,6)
            args = ThrowNumbers(itertools.chain([2,3,5,7,11]), t)

        if reverse: self.quiz.flip()
        """

    def is_equal(self, inp1, inp2, additional_tests=lambda x,y: True):
        if str(inp1) != str(self.question.problem):
            if isinstance(inp1, sp.Eq) and isinstance(inp2, sp.Eq):
                return sp.solve(inp1) == sp.solve(inp2)
            elif isinstance(inp1, sp.Expr) and isinstance(inp2, sp.Expr):
                return (str(inp1) == str(inp2)) or (sp.srepr(inp1) == sp.srepr(inp2))
        else:
            return False

    def start_game(self, current=None):
        self.state = 'not active'
        self.iteration_stopped = False
        self.starpacket.remove()
        if self.level is not None: self.level.remove()
        if self.finals_field is not None: self.finals_field.grid_forget()
        self.level = Level(self, self.tasks)

        if current is None: #autodetecting your level
            current = self.level.current
        self.kwargs = {'type': current, 'size': 10}

        for n in self.tasks:
            if n!= current:
                self.level.labels[n].configure(bg='SystemButtonFace')
            else: self.level.labels[n].configure(bg='green')
        if self.kwargs['type'] > self.tasks[-1]:
            awards_image = Image.open(r'images\awards.png').resize((30, 30), Image.ANTIALIAS)
            awards_photo = ImageTk.PhotoImage(awards_image)
            awards = Label(self.master, image=awards_photo)
            awards.grid(row=1, column=6, rowspan=2, sticky="nsew")
        else:
            self.update_quiz(**self.kwargs)  # problem expression appears
            self.timer = Timer(self.master)
            self.question = self.quiz.next()
            self.problem = Problem(self.master, Symform(self.question.problem))
            self.answer = Answer(self.master)
            self.score = 0
            self.symform = Symform('')
            self.inception_time = time.time()

    def react(self, x, master=None):
        if x=='OK':
            if self.state == 'active': #if self.problem is None:
                self.compile = False
                self.specialform = Specialform()
                if self.winner.field.grid_info(): self.winner.field.grid_remove()
                if self.loser.field.grid_info(): self.loser.field.grid_remove()
                if self.unclear.field.grid_info(): self.unclear.field.grid_remove()
                try:
                    self.question = self.quiz.next()
                    #print(self.question.problem, self.question.answer)
                    self.problem.update(Symform(self.question.problem))
                except StopIteration:
                    if not(self.iteration_stopped):
                        write('register.txt', self.kwargs['type'],
                              tuple(datetime.now().timetuple())[1:5],
                              round(time.time() - self.inception_time), self.score)
                        self.iteration_stopped = True

                    if self.score >= 9:
                        self.finals_photo = ImageTk.PhotoImage(self.finals_image1)
                        self.level = Level(self, self.tasks)
                    elif self.score >= 7: self.finals_photo = ImageTk.PhotoImage(self.finals_image2)
                    else: self.finals_photo = ImageTk.PhotoImage(self.finals_image3)
                    self.finals_field = Label(master, image=self.finals_photo)
                    self.finals_field.grid(row=1, column=6, rowspan=2, sticky="nsew")
                    self.problem.update(Symform(''))
                    self.answer.update(Symform(''))
                else:
                    self.symform = Symform('')
                    self.state = 'not active'
                    self.timer.reset()
            else:
                if self.specialform.state == 2: #COPYPASTING
                    self.specialform.state = 0
                    self.superbutton.button.configure(bg='#007f7f', text='·/·', relief='raised')
                    with sp.evaluate(False):
                        self.compile = True
                        self.symform.add(
                            f'{self.specialform.symform1.get_plain()}/{self.specialform.symform2.get_plain()}')
                try:
                    self.symform.tosympy()
                except Exception as e:
                    print('Exception: can''t convert input form to sympy expression')
                    self.unclear.field.grid(row=1, column=6, rowspan=2, sticky="nsew")
                else:
                    print(f'input converted to: {self.symform.get_sympy()}, correct input: {self.question.answer}')
                    if self.is_equal(self.symform.get_sympy(), self.question.answer):
                        self.score += 1
                        self.answer.check(True)
                        self.winner.field.grid(row=1, column=6, rowspan=2, sticky="nsew")
                        self.starpacket.credit(True)
                    else:
                        self.answer.check(False, symform = Symform(self.question.answer))
                        self.loser.field.grid(row=1, column=6, rowspan=2, sticky="nsew")
                        self.starpacket.credit(False)
                    self.state = 'active'

        elif x=='back':
            self.symform.rewind()
        elif x=='²':
            self.symform.add('^2')
        elif x=='·/·':
            #self.symform.plain += r'\frac{\cdot}{\dots}' #???
            if self.specialform.state == 0:
                self.specialform.state = 1
                self.superbutton.button.configure(bg='orange', text='▯/·', relief='groove')
                #self.symform.add(x)
            elif self.specialform.state == 1:
                self.specialform.state = 2
                self.superbutton.button.configure(bg='green', text='·/▯', relief='groove')
            elif self.specialform.state == 2:
                self.specialform.state = 0
                self.superbutton.button.configure(bg='#007f7f', text='·/·', relief='raised')
                '''self.specialform.symform1.tosympy()
                self.specialform.symform2.tosympy()
                nom = self.specialform.symform1.get_sympy()
                denom = self.specialform.symform2.get_sympy()'''
                with sp.evaluate(False):
                    self.compile = True
                    self.symform.add(f'{self.specialform.symform1.get_plain()}/{self.specialform.symform2.get_plain()}')
        else:
            if self.specialform.state != 0:
                self.specialform.add(x)
            else:
                self.symform.add(x)
        if self.state == 'not active':
            try:
                if self.specialform.state == 0:
                    self.answer.update(self.symform, compile=self.compile)
                elif self.specialform.state == 1:
                    if self.specialform.symform1.get_plain()=='':
                        specplain = r'\frac{\ }{\ }'
                    else:
                        specplain = r'\frac{' + self.specialform.symform1.get_plain()+r'}{\ }'
                    self.answer.update(Symform(self.symform.plain + specplain), compile=False)
                elif self.specialform.state == 2:
                    if self.specialform.symform1.get_plain() == '':
                        self.specialform.state = 1
                        self.superbutton.button.configure(bg='orange', text='▯/·', relief='groove')
                        raise ValueError
                    if self.specialform.symform2.get_plain() == '':
                        specplain = r'\frac{' + self.specialform.symform1.get_plain() + r'}{\ }'
                    else:
                        specplain = r'\frac{' + self.specialform.symform1.get_plain() + r'}{'+\
                        self.specialform.symform2.get_plain()+r'}'
                    self.answer.update(Symform(self.symform.plain + specplain), compile=False)
            except ValueError:
                print('Exception: cant display your input:', self.symform.plain)
                self.unclear.field.grid(row=1, column=6, rowspan=2, sticky="nsew")
                self.symform.plain = ''

class Level:
    def __init__(self, calc, levels, current=None):
        self.calc = calc
        self.master = calc.master
        self.levels = levels #allowed levels in current game
        self.current = current
        self.leveldone_image = Image.open(r'images\done.png').resize((20, 20), Image.ANTIALIAS)
        self.levelundone_image = Image.open(r'images\undone.png').resize((20, 20), Image.ANTIALIAS)
        self.levelpending_image = Image.open(r'images\pending.png').resize((20, 20), Image.ANTIALIAS)
        self.leveldone_photo = ImageTk.PhotoImage(self.leveldone_image)
        self.levelundone_photo = ImageTk.PhotoImage(self.levelundone_image)
        self.levelpending_photo = ImageTk.PhotoImage(self.levelpending_image)
        self.field = Frame(self.master)
        self.update()

    def response(self, i):
        self.calc.start_game(i)

    def update(self):
        #assuming levels preserves order and current >= levels[0]
        self.field.pack_forget()
        image = self.leveldone_photo
        labeling = False
        if self.current is None:
            self.current = self.identify_level()
        self.labels = dict()
        for i in self.levels:
            if i == self.current:
                image = self.levelpending_photo
                self.labels[i] = Button(self.field, image=image, command=lambda x=i: self.response(x), bg='green')
                self.labels[i].pack(side="left")
                image = self.levelundone_photo
                labeling = True
                continue
            if not(labeling):
                self.labels[i] = Button(self.field, image=image, command=lambda x=i: self.response(x))
                self.labels[i].pack(side="left")
            else:
                self.labels[i] = Label(self.field, image=image)
                self.labels[i].pack(side="left")
        self.field.grid(row=0, column=5, columnspan=2, sticky="nesw")

    def remove(self):
        for n in self.labels.values():
            n.pack_forget()

    def identify_level(self):
        return read('register.txt', pprint=False, allowed=self.levels)

root = Tk()
#root.grid_rowconfigure(0, minsize=20)
obj = Calc(root) #object instantiated
root.mainloop()

