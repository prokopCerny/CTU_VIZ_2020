import tkinter as tk
from pathlib import Path
import json
import numpy as np

def testClosure(stringVariable: tk.StringVar, labelText:str):
    def testClickListener(event):
        print(f'Clicked at {event.x}, {event.y}')
        stringVariable.set(labelText)
        print(event.widget.gettags(event.widget.find_withtag('current')))
    return testClickListener


class LabelCanvas(tk.Frame):
    def __init__(self, master, label, stringVariable):
        super().__init__(master=master, height=30)
        self.label = tk.Label(self, text=label, anchor='w', width=6)
        self.canvas = tk.Canvas(self, bg='blue', height=30)
        self.canvas.create_oval(0, 0, 20, 20, fill='red', tag='c1')
        self.canvas.tag_bind('c1', '<ButtonPress-1>', testClosure(stringVariable, f'{label} - circle1'))
        self.canvas.create_oval(20, 0, 40, 20, fill='red', tag='c2')
        self.canvas.tag_bind('c2', '<ButtonPress-1>', testClosure(stringVariable, f'{label} - circle2'))
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=False)
        self.canvas.pack(side=tk.RIGHT, fill=tk.X, expand=True)

class App:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.addButton = tk.Button(self.frame, text="New thingy", width=25, command=self.new_thing)
        self.removeButton = tk.Button(self.frame, text="Delete last thingy", width=25, command=self.delete_thing)
        self.topText = tk.StringVar()
        self.topTextLabel = tk.Label(self.frame, textvariable=self.topText)
        self.topText.set("Hello!")
        self.thingies = []
        self.topTextLabel.pack()
        self.addButton.pack()
        self.removeButton.pack()
        self.frame.pack(fill=tk.BOTH)

    def new_thing(self):
        if len(self.thingies) < 10:
            new_thing = LabelCanvas(self.frame, f'{len(self.thingies)}', self.topText)
            self.thingies.append(new_thing)
            new_thing.pack(fill=tk.X)

    def delete_thing(self):
        if self.thingies:
            last_thing = self.thingies.pop()
            last_thing.destroy()


if __name__ == '__main__':
    # with Path('./test.json').open(mode='r') as file:
    #     activations = np.array(json.loads(file.read()))
    # print(activations)

    window = tk.Tk()
    window.geometry("500x350+300+300")
    app = App(window)

    # canvas = tk.Canvas(window)
    # canvas.create_line(15, 25, 200, 25)
    # canvas.create_line(300, 35, 300, 200, dash=(4, 2))
    # canvas.create_line(55, 85, 155, 85, 105, 180, 55, 85)
    #
    # canvas.pack(fill=tk.BOTH, expand=1)
    # greeting = tk.Label(text="Hello, Tkinter")
    # lc = LabelCanvas(window, "Hey", greeting)
    # lc.pack(fill=tk.X)
    # lc2 = LabelCanvas(window, "Hoy_", greeting)
    # lc2.pack(fill=tk.X)
    #
    # greeting.pack()

    window.mainloop()