import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
        if not all(0 <= x <= 1 for x in vals):
            raise Exception("RGB1 values are not in range 0-1")
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
    def __init__(self, master, model, instance, stringVariable, neuron_activations, min_act, max_act, colormap=viridis):
        super().__init__(master=master, height=30)
        self.cmap = colormap
        self.label = tk.Label(self, text=instance, anchor='w', width=6)
        self.model = model
        self.instance = instance
        self.remove_button = tk.Button(self, text='X', command=lambda : self.model.remove(self.instance))
        self.canvas = tk.Canvas(self, height=30)
        self.cur_instance_neuron_activations = neuron_activations
        self.min = min_act
        self.max = max_act
        self.circles = [self.canvas.create_oval(6+num*23, 6, 6+20+num*23, 6+20, fill=RGBtoHex(self.cmap((v-self.min)/(self.max-self.min))))
                        for (num, v)
                        in enumerate(self.cur_instance_neuron_activations)]
        for num, (circle, activation) in enumerate(zip(self.circles, self.cur_instance_neuron_activations)):
            self.canvas.tag_bind(circle,
                                 '<ButtonPress-1>',
                                 setStringVarEventHandlerClosure(stringVariable,
                                                                 f'{instance} - Neuron {num + 1}: {activation}'))
        self.remove_button.pack(side=tk.LEFT, expand=False)
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=False)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def update_max_min(self, max, min):
        """Update brightness relative to maximum observed value"""
        if self.max != max or self.min != min:
            self.max, self.min = max, min
            for cur_activation, circle in zip(self.cur_instance_neuron_activations, self.circles):
                v = (cur_activation-self.min)/(self.max-self.min)
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


def compute_needed_width_for_neurons(layer_data):
    first_instance_key = next(iter(layer_data))
    neuron_count = len(layer_data[first_instance_key])
    return 6+5+67+neuron_count*23


class LayerActivationWindow(tk.Toplevel):
    # TODO: CLEANUP CODE AND IMPROVE NAMING
    def __init__(self, master, model: DataModel, layer_identifier: str):
        tk.Toplevel.__init__(self, master=master)
        self.model = model
        self.layer = layer_identifier
        self.selected_data = self.model.data['activations'][self.layer]

        self.topText = tk.StringVar()
        self.frame_for_top_label_alignment = tk.Frame(self)
        self.topTextLabel = tk.Label(self.frame_for_top_label_alignment, anchor='w', textvariable=self.topText)
        self.topText.set("Click on a neuron!")

        self.frame_for_top_label_alignment.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.topTextLabel.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self)
        self.v_scrollbar = tk.Scrollbar(self, command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self, command=self.canvas.xview, orient='horizontal')
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.frame = tk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        self.canvas.itemconfig(self.canvas_frame, width=compute_needed_width_for_neurons(self.selected_data))

        self.frame.bind('<Configure>', lambda event: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        # self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfig(self.canvas_frame, width=event.width))

        self.neuron_activations = {}
        self.maxes = {}  # list of max neuron activation per each digit, used for value normalization for coloring
        self.mins = {}

        self.recreate_from_model()
        self.model.observers.append(self)
        self.protocol("WM_DELETE_WINDOW", self._quit_window)

    def _quit_window(self):
        self.model.observers.remove(self)
        self.destroy()

    def _add_instance(self, instance):
        if instance not in self.neuron_activations:
            self.maxes[instance] = np.max(self.selected_data[instance])
            self.mins[instance] = np.min(self.selected_data[instance])
            cur_max = max(self.maxes.values())
            cur_min = min(self.mins.values())
            new_thing = NeuronActivationCircles(self.frame, self.model, instance, self.topText, self.selected_data[instance],cur_min, cur_max)
            self.neuron_activations[instance] = new_thing
            new_thing.pack(fill=tk.X, expand=True)
            for thing in self.neuron_activations.values():
                thing.update_max_min(cur_max, cur_min)

    def _remove_instance(self, instance):
        if instance in self.neuron_activations:
            self.neuron_activations[instance].destroy()
            del self.neuron_activations[instance]
        if instance in self.maxes:
            del self.maxes[instance]
            del self.mins[instance]
            if self.maxes:
                cur_max = max(self.maxes.values())
                cur_min = min(self.mins.values())
                for thing in self.neuron_activations.values():
                    thing.update_max_min(cur_max, cur_min)

    def notify(self, event):
        if isinstance(event, ModelEvent):
            if event.type == ModelEventType.ADD:
                self._add_instance(event.data)
            elif event.type == ModelEventType.REMOVE:
                self._remove_instance(event.data)

    def recreate_from_model(self):
        while self.neuron_activations:
            instance = next(iter(self.neuron_activations))
            self._remove_instance(instance)
        for digit in self.model.selected:
            self._add_instance(digit)


class ImageWindow(tk.Frame):
    def __init__(self, master, model, instance, width=100, height=100, image_scale=1):
        super().__init__(master=master)
        self.w = width
        self.h = height
        self.scale = image_scale
        self.model = model
        self.canvas = None
        self.update_canvas(instance)

    def update_canvas(self, instance):
        if self.canvas is not None:
            self.canvas.destroy()
        image_data = self.model.data['images'][instance]
        im_h, im_w = image_data.shape
        imag = Image.fromarray(np.round(image_data*255)).resize(size=(im_h*self.scale, im_w*self.scale), resample=Image.NEAREST)
        img = ImageTk.PhotoImage(image=imag)
        self.canvas = tk.Canvas(self,width=self.w,height=self.h) #tk.Canvas(master, width=300, height=300)
        self.canvas.pack()
        self.canvas.pic=img
        self.canvas.create_image(0,0, anchor="nw", image=img)


class ImageSelector(tk.Frame):
    def __init__(self, master, model):
        super().__init__(master=master)
        self.model = model
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.digit_buttons = [tk.Button(self.top_frame,
                                        text=f'{digit}',
                                        command=self.button_callback_closure(digit))
                              for digit in range(10)]
        for button in self.digit_buttons:
            button.pack(side=tk.LEFT)
        self.lbl = tk.Label(self.top_frame, text="TSTS")
        self.lbl.pack(side=tk.RIGHT)
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.scroll_canvas = self.h_scrollbar = None
        self.show_numbers(0)

    def button_callback_closure(self, digit:int):
        return lambda: self.show_numbers(digit)

    def show_numbers(self, digit: int):
        if self.scroll_canvas is not None:
            self.scroll_canvas.destroy()
        if self.h_scrollbar is not None:
            self.h_scrollbar.destroy()
        self.scroll_canvas = tk.Canvas(self.bottom_frame)
        self.h_scrollbar = tk.Scrollbar(self.bottom_frame, command=self.scroll_canvas.xview, orient='horizontal')
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.scroll_canvas.configure(xscrollcommand=self.h_scrollbar.set)
        self.canvas_frame = tk.Frame(self.scroll_canvas)
        self.canvas_window = self.scroll_canvas.create_window((0,0), window=self.canvas_frame, anchor='nw')
        self.canvas_frame.bind('<Configure>',
                               lambda event: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox('all')))

        self.imags = [ImageWindow(self.canvas_frame, self.model, instance, width=84 ,height=84, image_scale=3)
                      for idx, instance
                      in enumerate(self.model.data['digit_to_instances'][str(digit)])
                      if idx < 50]
        for imag in self.imags:
            imag.pack(side=tk.LEFT)


class MainWindow:
    def __init__(self, master, model: DataModel):
        self.selector_window = ImageSelector(tk.Toplevel(master), model)
        self.selector_window.pack(fill=tk.BOTH, expand=True)
        self.image_window = ImageWindow(tk.Toplevel(master), model, next(iter(model.data['images'])), width=300, height=300, image_scale=10)
        self.image_window.pack()

        self.master = master
        self.model = model

        self.label = tk.Label(self.master, text="Digit:", anchor='w')
        self.entry = tk.Entry(self.master)
        self.entry.insert(tk.END, "0")
        self.addButton = tk.Button(self.master, text="Add digit activations", width=25,
                                   command=self.read_add_digit)
        self.removeButton = tk.Button(self.master, text="Delete max digit activations", width=25,
                                      command=self.delete_max_digit_activations)

        self.sep = ttk.Separator(self.master, orient=tk.HORIZONTAL)

        self.activation_windows = {}
        self.layer_buttons = [tk.Button(self.master,
                                        text=f'{layer} activations',
                                        width=25,
                                        command=self.open_activation_window_closure(layer))
                              for layer
                              in self.model.data['activations'].keys()]

        self.label.pack()
        self.entry.pack()
        self.addButton.pack()
        self.removeButton.pack()
        self.sep.pack(fill=tk.X, pady=5)
        for button in self.layer_buttons:
            button.pack()

    def open_activation_window_closure(self, layer:str):
        return lambda: self.activation_window_open(layer)

    def read_add_digit(self):
        txt = self.entry.get()
        if txt and txt.isdigit():
            digit = int(txt)
            if 0 <= digit < 10:
                self.model.select(f'Digit {digit}')
                self.image_window.update_canvas(f'Digit {digit}')
                # self.update_canvas(f'Digit {digit}')
                self.entry.delete(0, tk.END)
                self.entry.insert(0, f'{digit+1}')

    def delete_max_digit_activations(self):
        if self.model.selected:
            max_digit = max(self.model.selected)
            self.model.remove(max_digit)

    def activation_window_open(self, identifier: str):
        try:
            if self.activation_windows[identifier].state() == "normal":
                self.activation_windows[identifier].focus()
        except (KeyError, tk.TclError):
            new_window = LayerActivationWindow(self.master, self.model, identifier)
            instances = self.model.data['activations'][identifier]

            new_window.geometry(f'{min(compute_needed_width_for_neurons(instances)+20, 1250)}x400+300+300')
            new_window.title(f'{identifier} activations')
            self.activation_windows[identifier] = new_window


if __name__ == '__main__':
    # TODO: split into more files, rename from gui_test

    # a json is needed containing the average activations for all digits in the first fully connected layer
    # can be created using the jupyter notebook
    with Path('./NN_data.json').open(mode='r') as file:
        network_data = json.loads(file.read())
    # print(activations)

    for key in network_data['images'].keys():
        network_data['images'][key] = np.array(network_data['images'][key])

    model = DataModel(network_data)

    # *model.selected, = (f'Digit {x}' for x in range(10))

    root = tk.Tk()
    image_data = network_data['images'][next(iter(network_data['images']))]
    # print(root.tk)
    # window.geometry("1550x450+300+300")

    app = MainWindow(root, model)

    root.mainloop()
