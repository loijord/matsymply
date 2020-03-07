from creator import Creator
from tkinter import Button, Tk, font, Label
from PIL import Image, ImageDraw, ImageFont, ImageTk
from time import time
import random
import itertools
from matplotlib import use
use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import sympy as sp #pprint, latex, Rational
transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
import json

class Picture:
    def __init__(self, image=None):
        self.image = image #Image.open instance

    def __add__(self, other):
        images = [self.image, other.image]
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new('RGB', (total_width, max_height), (64, 160, 224))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, (max_height-im.size[1])//2))
            x_offset += im.size[0]
        return Picture(new_im)

    def textconcat_image(self, text, textcolor=(255,255,255), imagecolor=(64, 160, 224)):
        if 'frac' in text:
            text = [text[:text.index('frac')], text[text.index('frac'):9+text.index('frac')], text[9+text.index('frac'):]]
        else:
            text=[text]

        picture = Picture(self.text_image(text[0]))
        for n in text[1:]:
            picture = picture + Picture(self.text_image(n))
        return picture.image

    def text_image(self, text, textcolor=(255,255,255), imagecolor=(64, 160, 224)):
        font = ImageFont.truetype("arial", 30)
        text_size = font.getsize(text)
        img = Image.new('RGB', text_size, imagecolor)
        d = ImageDraw.Draw(img)
        d.text((0, 0), text, font=font, fill=textcolor)
        return img

"""class ThrowNumbers:
    def __init__(self, possibles, size, type='distinct'):
        if type == 'distinct':
            self.out = random.sample(list(itertools.permutations(possibles, size)))
        if type == 'any':
            self.out = random.choice(list(itertools.product(possibles, repeat=size)))"""

class Timer:
    def __init__(self, master):
        self.master = master
        self.time = time()
        self.field = Label(master, text='0', width=3,
                           fg="#{0:02x}{1:02x}{2:02x}".format(255, 255, 255),
                           font=font.Font(family='Helvetica', weight='bold', size=20),
                           bg="#{0:02x}{1:02x}{2:02x}".format(32, 80, 96),
                           borderwidth=5, relief="groove", anchor="e")
        self.field.grid(row=1, column=1, rowspan=2)
        self.update()

    def update(self):
        now = round(time() - self.time)
        self.field.configure(text=now)
        self.master.after(1000, self.update)

    def reset(self):
        self.time = time()

class Problem:
    def __init__(self, master, expr):
        #shoul be initialized from expression[not possible] or text form[used]
        self.master = master
        self.field = Label(master, width=15,
                                   fg="#{0:02x}{1:02x}{2:02x}".format(255, 255, 255),
                                   font=font.Font(family='Helvetica', weight='bold', size=20),
                                   bg="#{0:02x}{1:02x}{2:02x}".format(128, 128, 96),
                                   borderwidth=5, relief="raised")
        self.field.grid(row=1, column=2, columnspan=3, sticky="nesw")
        self.update(expr)

    def update(self, expr): #r'x\sqrt{\frac{3}{4}}'
        fig = Figure(figsize=(5, 1), dpi=50, facecolor='yellow')
        ax = fig.gca()
        ax.clear()
        ax.text(0.0, 0.0, "$" + sp.latex(expr) + "$", fontsize=40), #bbox=dict(facecolor='red', alpha=0.5))
        ax.axis('off')
        # for item in [ax, fig]: item.patch.set_visible(False)
        ax.get_xaxis().set_visible(True)
        ax.get_yaxis().set_visible(True)

        canvas = FigureCanvasTkAgg(fig, master=self.field)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.configure(background='red', highlightcolor='green', highlightbackground='blue')
        canvas_widget.grid(row=1, column=2, columnspan=3, sticky="nesw")
        fig.tight_layout(pad=1)
        canvas.draw()

class Response:
    def __init__(self, master, image_name):
        #winner.png, loser.png
        self.image = ImageTk.PhotoImage(Image.open(image_name).resize((70, 70), Image.ANTIALIAS))
        self.photo = Label(master, image=self.image)
        self.photo.image = self.image
        self.field = Label(master, image=self.image)

class Answer:
    def __init__(self, master):
        self.master = master
        self.field = Label(master, activebackground='red',
                                  fg="#{0:02x}{1:02x}{2:02x}".format(0, 64, 0),
                                  bg="#{0:02x}{1:02x}{2:02x}".format(64, 160, 224),
                                  borderwidth=5, relief="ridge")
        # "flat", "raised", "sunken", "ridge", "solid", and "groove"
        self.field.grid(row=2, column=2, columnspan=3, sticky="nesw")
        self.fig = None
        self.ax = None
        self.canvas = None

    def update(self, text):
        #not parses text, displays latex form as it is
        fig = Figure(figsize=(5, 1), dpi=50)
        ax = fig.gca()

        if text != '': text = "$" + sp.latex(text) + "$"
        print('Error', text)
        self.txt = ax.text(0.0, 0.0, text, fontsize=40)#, bbox=dict(facecolor='red', alpha=0.5))
        ax.axis('off')

        self.canvas = FigureCanvasTkAgg(fig, master=self.field)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(background='red', highlightcolor='green', highlightbackground='blue')
        canvas_widget.grid(row=1, column=2, columnspan=3, sticky="nesw")
        try:
            fig.tight_layout(pad=1)
            self.fig, self.ax = fig, ax
        except ValueError:
            self.fig.patch.set_facecolor('#900000')
        self.canvas.draw()

    def check(self, is_good, correct=None):
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
            self.ax.text(0.0, -1.5, "$" + correct + "$", fontsize=40)
            self.canvas.draw()


class Key:
    def __init__(self, master, text, color, command, **kwargs):
        self.master = master
        self.state = 'active' #at first its active cuz problem is being solved

        font = ImageFont.truetype("arial", 30)
        self.button = Button(master, text=text,
                             command=lambda x=text: command(x),
                             bg="#{0:02x}{1:02x}{2:02x}".format(*color), **kwargs)
        self.button.grid(row=4, column=1)  # columnspan=2)

class Calc:
    def __init__(self, master):
        """Constructor method"""
        self.master = master
        self.master.title('Calulator')
        self.master.geometry()
        self.state = 'not active'
        self.star_image = None
        self.emptystar_image = Image.open(r'emptystar.png').resize((30, 30), Image.ANTIALIAS)
        self.fullstar_image = Image.open(r'fullstar.png').resize((30, 30), Image.ANTIALIAS)
        self.general_str=''
        with open('settings.txt', 'r') as f:
            self.kwargs = {**json.load(f), 'size':10}
            print(self.kwargs)

        self.update_quiz(**self.kwargs) # problem expression appears

        self.timer = Timer(master)
        self.master.rowconfigure(1, weight=1)

        self.problem_expr, self.answer_expr = self.quiz.next()
        self.problem = Problem(master, self.problem_expr)
        self.answer = Answer(master)

        #this is just in case for empty space if solution extends
        #self.waste_field = Label()
        #self.waste_field.grid(row=3, column=2, columnspan=3)

        self.winner = Response(master, 'winner.png')
        self.loser = Response(master, 'loser.png')

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


    def credit(self, master, correctness):
        if self.star_image is None:
            if correctness:
                self.star_image = Picture(self.fullstar_image).image
            else:
                self.star_image = Picture(self.emptystar_image).image

            self.star_photo = ImageTk.PhotoImage(self.star_image)
            self.stars_field = Label(master, image=self.star_photo)
            self.stars_field.grid(row=0, column=0, columnspan=5, sticky='W')
        else:
            if correctness:
                self.star_image = (Picture(self.star_image) + Picture(self.fullstar_image)).image
            else:
                self.star_image = (Picture(self.star_image) + Picture(self.emptystar_image)).image
            self.star_photo = ImageTk.PhotoImage(self.star_image)
            self.stars_field.configure(image=self.star_photo)

    def react(self, x, master=None):
        if x=='OK':
            if self.state == 'active': #if self.problem is None:
                if self.winner.field.grid_info(): self.winner.field.grid_remove()
                if self.loser.field.grid_info(): self.loser.field.grid_remove()
                self.problem_expr, self.answer_expr = self.quiz.next()
                self.problem.update(self.problem_expr)
                self.general_str = ''
                self.state = 'not active'
                self.timer.reset()
            else:
                try:
                    if self.general_str != '':
                        input_expr = parse_expr(self.general_str, transformations=transformations)
                    print(f'input converted to: {input_expr}, correct input: {self.answer_expr}')
                    if self.general_str != '' and input_expr == self.answer_expr:
                        self.answer.check(True)
                        self.winner.field.grid(row=1, column=5, rowspan=2, sticky="nsew")
                        self.credit(master, True)
                    else:
                        self.answer.check(False, correct = sp.latex(self.answer_expr))
                        self.loser.field.grid(row=1, column=5, rowspan=2, sticky="nsew")
                        self.credit(master, False)
                    self.state = 'active'
                except (SyntaxError, ValueError):
                    #SyntaxError is raised when you input 6(+)
                    #ValueError is raised when you put consequitive superscripts
                    self.answer.fig.patch.set_facecolor('#900000')
                    self.answer.canvas.draw()
                    raise SyntaxError

        elif x=='back':
            if len(self.general_str):
                if self.general_str[-2:]=='^2':
                    self.general_str = self.general_str[:-2]
                else:
                    self.general_str=self.general_str[:-1]
        else:
            if x=='²': self.general_str += '^2'
            else: self.general_str += x
        if self.state == 'not active':
            self.answer.update(self.general_str)

root = Tk()
#root.grid_rowconfigure(0, minsize=20)
obj = Calc(root) #object instantiated
root.mainloop()

