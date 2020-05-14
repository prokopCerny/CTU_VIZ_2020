import tkinter as tk
from pathlib import Path
import json
import numpy as np

def testClosure(textLabel, *specialData):
    def testClickListener(event):
        print(f'Clicked at {event.x}, {event.y}')
        print(specialData)
        textLabel.configure(text=str(specialData))
        print(event.widget.gettags(event.widget.find_withtag('current')))
    return testClickListener


class LabelCanvas(tk.Frame):
    def __init__(self, parent, label, textLabel):
        super().__init__(height=30)
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text=label, anchor='w', width=3)
        self.canvas = tk.Canvas(self, bg='blue', height=30)
        self.canvas.create_oval(0, 0, 20, 20, fill='red', tag='c1')
        self.canvas.tag_bind('c1', '<ButtonPress-1>', testClosure(textLabel, label, "AAA", 1))
        self.canvas.create_oval(20, 0, 40, 20, fill='red', tag='c2')
        self.canvas.tag_bind('c2', '<ButtonPress-1>', testClosure(textLabel, label, "BBB", 2))
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=False)
        self.canvas.pack(side=tk.RIGHT, fill=tk.X, expand=False)

if __name__ == '__main__':
    # with Path('./test.json').open(mode='r') as file:
    #     activations = np.array(json.loads(file.read()))
    # print(activations)
    window = tk.Tk()
    window.geometry("500x350+300+300")
    # canvas = tk.Canvas(window)
    # canvas.create_line(15, 25, 200, 25)
    # canvas.create_line(300, 35, 300, 200, dash=(4, 2))
    # canvas.create_line(55, 85, 155, 85, 105, 180, 55, 85)
    #
    # canvas.pack(fill=tk.BOTH, expand=1)
    greeting = tk.Label(text="Hello, Tkinter")
    lc = LabelCanvas(window, "Hey", greeting)
    lc.pack()
    lc2 = LabelCanvas(window, "Hoy_", greeting)
    lc2.pack()

    greeting.pack()
    window.mainloop()