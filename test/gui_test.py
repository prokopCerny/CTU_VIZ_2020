import tkinter as tk
from pathlib import Path
import json
import numpy as np
from colormaps import viridis, plasma, inferno, magma
from enum import Enum


# Stolen from stackoverflow TODO: rewrite shorter
def RGBtoHex(vals, rgbtype=1):
    """Converts RGB values in a variety of formats to Hex values.

       :param  vals:     An RGB/RGBA tuple
       :param  rgbtype:  Valid values are:
                            1 - Inputs are in the range 0 to 1
                          256 - Inputs are in the range 0 to 255

       :return A hex string in the form '#RRGGBB' or '#RRGGBBAA'
  """

    if len(vals) != 3 and len(vals) != 4:
        raise Exception("RGB or RGBA inputs to RGBtoHex must have three or four elements!")
    if rgbtype != 1 and rgbtype != 256:
        raise Exception("rgbtype must be 1 or 256!")

    #Convert from 0-1 RGB/RGBA to 0-255 RGB/RGBA
    if rgbtype == 1:
        vals = [255 * x for x in vals]

    #Ensure values are rounded integers, convert to hex, and concatenate
    return '#' + ''.join([f'{int(round(x)):02X}' for x in vals])


class ModelEventType(Enum):
    ADD, REMOVE = range(2)


class ModelEvent:
    type: ModelEventType

    def __init__(self, type: ModelEventType, data=None):
        self.type = type
        self.data = data


class DataModel:
    def __init__(self, data):
        self.selected = []
        self.data = data
        self.observers = []

    def select(self, identifier):
        if identifier not in self.selected:
            self.selected.append(identifier)
            self._notify_observers(ModelEvent(ModelEventType.ADD, data=identifier))

    def remove(self, identifier):
        if identifier in self.selected:
            self.selected.remove(identifier)
            self._notify_observers(ModelEvent(ModelEventType.REMOVE, data=identifier))

    def _notify_observers(self, event: ModelEvent):
        for observer in self.observers:
            observer.notify(event)


def setStringVarEventHandlerClosure(stringVariable: tk.StringVar, text:str):
    def setStringVarEventHandler(event):
        print(f'Clicked at {event.x}, {event.y}')
        stringVariable.set(text)
        #print(event.widget.itemconfig(event.widget.find_withtag('current'), fill='green'))
    return setStringVarEventHandler


class NeuronActivationCircles(tk.Frame):
    def __init__(self, master, label, stringVariable, neuron_activations, max_act, colormap=viridis):
        super().__init__(master=master, height=30)
        self.cmap = colormap
        self.label = tk.Label(self, text=label, anchor='w', width=6)
        self.canvas = tk.Canvas(self, height=30)
        self.cur_instance_neuron_activations = neuron_activations
        self.max = max_act
        self.circles = [self.canvas.create_oval(6+num*23, 6, 6+20+num*23, 6+20, fill=RGBtoHex(self.cmap(v/self.max)))
                        for (num, v)
                        in enumerate(self.cur_instance_neuron_activations)]
        for num, (circle, activation) in enumerate(zip(self.circles, self.cur_instance_neuron_activations)):
            self.canvas.tag_bind(circle,
                                 '<ButtonPress-1>',
                                 setStringVarEventHandlerClosure(stringVariable,
                                                                 f'{label} - Neuron {num + 1}: {activation}'))
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=False)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def update_max(self, max):
        """Update brightness relative to maximum observed value"""
        if self.max != max:
            self.max = max
            for cur_activation, circle in zip(self.cur_instance_neuron_activations, self.circles):
                v = cur_activation/max
                self.canvas.itemconfig(circle, fill=RGBtoHex(self.cmap(v)))


def find_smallest_missing(lst):
    if lst:
        if lst[0] != 0:
            return 0
        else:
            for i in range(len(lst)-1):
                if lst[i+1] - lst[i] > 1:
                    return lst[i] + 1
            return lst[-1]+1
    else:
        return 0


class App:
    # TODO: CLEANUP CODE AND IMPROVE NAMING
    def __init__(self, master, model: DataModel):
        self.master = master
        self.model = model
        self.frame = tk.Frame(self.master)
        self.entry = tk.Entry(self.frame)
        self.addButton = tk.Button(self.frame, text="Add digit activations", width=25,
                                   command=self.read_add_digit)
        self.removeButton = tk.Button(self.frame, text="Delete max digit activations", width=25,
                                      command=self.delete_max_digit_activations)
        self.recBtn = tk.Button(self.frame, text="Recreate", width=25, command=self.recreate_from_model)
        self.topText = tk.StringVar()
        self.topTextLabel = tk.Label(self.frame, textvariable=self.topText)
        self.topText.set("Click on a neuron!")
        self.neuron_activations = {}
        self.topTextLabel.pack()
        self.entry.pack()
        self.addButton.pack()
        self.removeButton.pack()
        self.recBtn.pack()
        self.frame.pack(fill=tk.BOTH)
        self.maxes = {}  # list of max neuron activation per each digit, used for value normalization for coloring
        self.recreate_from_model()
        self.model.observers.append(self)

    def _add_instance(self, instance):
        if instance not in self.neuron_activations:
            self.maxes[instance] = np.max(self.model.data[instance])
            cur_max = max(self.maxes.values())
            new_thing = NeuronActivationCircles(self.frame, f'Digit {instance}', self.topText, self.model.data[instance], cur_max)
            self.neuron_activations[instance] = new_thing
            new_thing.pack(fill=tk.X)
            for thing in self.neuron_activations.values():
                thing.update_max(cur_max)

    def _remove_instance(self, instance):
        if instance in self.neuron_activations:
            self.neuron_activations[instance].destroy()
            del self.neuron_activations[instance]
        if instance in self.maxes:
            del self.maxes[instance]
            if self.maxes:
                cur_max = max(self.maxes.values())
                for thing in self.neuron_activations.values():
                    thing.update_max(cur_max)

    def notify(self, event):
        if isinstance(event, ModelEvent):
            if event.type == ModelEventType.ADD:
                self._add_instance(event.data)
            elif event.type == ModelEventType.REMOVE:
                self._remove_instance(event.data)

    def read_add_digit(self):
        txt = self.entry.get()
        if txt and txt.isdigit():
            digit = int(txt)
            if 0 <= digit < 10:
                self.model.select(digit)
                self.entry.delete(0, tk.END)
                self.entry.insert(0, f'{digit+1}')

    def delete_max_digit_activations(self):
        if self.neuron_activations:
            max_digit = max(self.neuron_activations.keys())
            self.model.remove(max_digit)

    def recreate_from_model(self):
        while self.neuron_activations:
            instance = next(iter(self.neuron_activations))
            self._remove_instance(instance)
        for digit in self.model.selected:
            self._add_instance(digit)


if __name__ == '__main__':
    # TODO: split into more files, rename from gui_test

    # a json is needed containing the average activations for all digits in the first fully connected layer
    # can be created using the jupyter notebook
    with Path('./test.json').open(mode='r') as file:
        activations = np.array(json.loads(file.read()))
    # print(activations)

    # TODO: think up the correct JSON structure for storing the data, something like the dict below
    data = {digit: activations[digit] for digit in range(10)}
    model = DataModel(data)
    print(model.data[0])
    model.selected = [0, 4, 6]

    window = tk.Tk()
    window.geometry("1550x450+300+300")
    app = App(window, model)

    window.mainloop()
