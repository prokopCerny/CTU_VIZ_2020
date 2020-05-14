import tkinter as tk
from pathlib import Path
import json
import numpy as np


# Stolen from stackoverflow TODO: rewrite shorter
def RGBtoHex(vals, rgbtype=1):
    """Converts RGB values in a variety of formats to Hex values.

       @param  vals     An RGB/RGBA tuple
       @param  rgbtype  Valid values are:
                            1 - Inputs are in the range 0 to 1
                          256 - Inputs are in the range 0 to 255

       @return A hex string in the form '#RRGGBB' or '#RRGGBBAA'
  """

    if len(vals)!=3 and len(vals)!=4:
        raise Exception("RGB or RGBA inputs to RGBtoHex must have three or four elements!")
    if rgbtype!=1 and rgbtype!=256:
        raise Exception("rgbtype must be 1 or 256!")

    #Convert from 0-1 RGB/RGBA to 0-255 RGB/RGBA
    if rgbtype==1:
        vals = [255*x for x in vals]

    #Ensure values are rounded integers, convert to hex, and concatenate
    return '#' + ''.join([f'{int(round(x)):02X}' for x in vals])


def setStringVarEventHandlerClosure(stringVariable: tk.StringVar, text:str):
    def setStringVarEventHandler(event):
        print(f'Clicked at {event.x}, {event.y}')
        stringVariable.set(text)
        #print(event.widget.itemconfig(event.widget.find_withtag('current'), fill='green'))
    return setStringVarEventHandler


class NeuronActivationCircles(tk.Frame):
    def __init__(self, master, label, stringVariable, digit, data, max):
        super().__init__(master=master, height=30)
        self.label = tk.Label(self, text=label, anchor='w', width=6)
        self.canvas = tk.Canvas(self, height=30)
        self.digit = digit
        self.cur_digit_neuron_activations = data[digit]
        self.max = max
        self.circles = [self.canvas.create_oval(6+num*23, 6, 6+20+num*23, 6+20, fill=RGBtoHex((v/max, v/max, v/max))) for (num, v) in enumerate(data[digit])]
        for num, circle in enumerate(self.circles):
            self.canvas.tag_bind(circle, '<ButtonPress-1>', setStringVarEventHandlerClosure(stringVariable, f'Digit {digit} - Neuron {num + 1}: {data[digit, num]}'))
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=False)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def update_max(self, max):
        """Update brightness relative to maximum observed value"""
        if self.max != max:
            self.max = max
            for cur_activation, circle in zip(self.cur_digit_neuron_activations, self.circles):
                v = cur_activation/max
                self.canvas.itemconfig(circle, fill=RGBtoHex((v, v, v)))


class App:
    # TODO: CLEANUP CODE AND IMPROVE NAMING
    def __init__(self, master, data):
        self.master = master
        self.data = data
        self.frame = tk.Frame(self.master)
        self.addButton = tk.Button(self.frame, text="Add digit activations", width=25,
                                   command=self.next_digit_activations)
        self.removeButton = tk.Button(self.frame, text="Delete last digit activations", width=25,
                                      command=self.delete_last_digit_activations)
        self.topText = tk.StringVar()
        self.topTextLabel = tk.Label(self.frame, textvariable=self.topText)
        self.topText.set("Click on a neuron!")
        self.digit_activations = []
        self.topTextLabel.pack()
        self.addButton.pack()
        self.removeButton.pack()
        self.frame.pack(fill=tk.BOTH)
        self.maxes = []  # list of max neuron activation per each digit, used for value normalization for coloring

    def next_digit_activations(self):
        if len(self.digit_activations) < 10:
            digit = len(self.digit_activations)
            self.maxes.append(np.max(self.data[digit]))
            cur_max = np.max(self.maxes)
            new_thing = NeuronActivationCircles(self.frame, f'Digit {digit}', self.topText, digit, self.data, cur_max)
            self.digit_activations.append(new_thing)
            new_thing.pack(fill=tk.X)
            for thing in self.digit_activations:
                thing.update_max(cur_max)

    def delete_last_digit_activations(self):
        if self.digit_activations:
            last_thing = self.digit_activations.pop()
            last_thing.destroy()
            self.maxes.pop()
            if self.maxes:
                cur_max = np.max(self.maxes)
                for thing in self.digit_activations:
                    thing.update_max(cur_max)


if __name__ == '__main__':
    # a json is needed containing the average activations for all digits in the first fully connected layer
    # can be created using the jupyter notebook
    with Path('./test.json').open(mode='r') as file:
        activations = np.array(json.loads(file.read()))
    print(activations)

    window = tk.Tk()
    window.geometry("1550x450+300+300")
    app = App(window, activations)

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
