import matplotlib.pyplot as plt
from tkinter import Tk, Label
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fig = Figure(figsize=(6.6, 1), dpi=50, facecolor='yellow')
ax = fig.gca()
ax.clear()
ax.text(0.0, 0.0, r'$\frac{\ }{\ }$', fontsize=40)
ax.axis('off')

root = Tk()
label = Label(root)
label.grid(sticky="nesw")
canvas = FigureCanvasTkAgg(fig, master=label)
canvas_widget = canvas.get_tk_widget()
canvas_widget.configure(background='red', highlightcolor='green', highlightbackground='blue')
canvas_widget.grid(sticky="nesw")
fig.tight_layout(pad=1)
canvas.draw()

root.mainloop()