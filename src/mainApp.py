import tkinter as tk
from tkinter import ttk

from pathlib import Path
import json
import numpy as np

from datamodel import DataModel, ModelEvent, ModelEventType
from image_frame import ImageFrame
from image_gallery import ImageSelectorGallery
from layer_activations_window import LayerActivationsWindow
from utils import compute_needed_width_for_neurons, get_average_digit_instance_name


class MenuPanel(tk.Frame):
    def __init__(self, master, model):
        super().__init__(master=master)
        self.model = model
        self.label = tk.Label(self, text="Digit:", anchor='w')
        self.entry = tk.Entry(self)
        self.entry.insert(tk.END, "0")
        self.addButton = tk.Button(self, text="Add digit activations", width=25,
                                   command=self.read_add_digit)
        self.removeButton = tk.Button(self, text="Delete max digit activations", width=25,
                                      command=self.delete_max_digit_activations)

        self.sep = ttk.Separator(self, orient=tk.HORIZONTAL)

        self.activation_windows = {}
        self.layer_buttons = [tk.Button(self,
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

    def activation_window_open(self, identifier: str):
        try:
            if self.activation_windows[identifier].state() == "normal":
                self.activation_windows[identifier].focus()
        except (KeyError, tk.TclError):
            new_window = LayerActivationsWindow(self.master, self.model, identifier)
            instances = self.model.data['activations'][identifier]

            new_window.geometry(f'{min(compute_needed_width_for_neurons(instances) + 20, 1250)}x400+300+300')
            new_window.title(f'{identifier} activations')
            self.activation_windows[identifier] = new_window

    def open_activation_window_closure(self, layer:str):
        return lambda: self.activation_window_open(layer)

    def read_add_digit(self):
        txt = self.entry.get()
        if txt and txt.isdigit():
            digit = int(txt)
            if 0 <= digit < 10:
                instance_name = get_average_digit_instance_name(digit)
                self.model.add(instance_name)
                self.model.select(instance_name)
                # self.update_canvas(f'Digit {digit}')
                self.entry.delete(0, tk.END)
                self.entry.insert(0, f'{digit+1}')

    def delete_max_digit_activations(self):
        if self.model.selected_instances:
            max_digit = max(self.model.selected_instances)
            self.model.remove(max_digit)


category10 = ["#1f77b4",
              "#ff7f0e",
              "#2ca02c",
              "#d62728",
              "#9467bd",
              "#8c564b",
              "#e377c2",
              "#7f7f7f",
              "#bcbd22",
              "#17becf"]


class ScatterCanvas(tk.Canvas):
    def __init__(self, master, model, layer, width, height, circle_radius=3, padding=4, **kw):
        super().__init__(master, width=width, height=height, **kw)
        self.model = model
        self.layer = layer

        w, h = width, height
        self.configure(scrollregion=(-w/2, -h/2, w/2, h/2))  # make origin the middle

        names, coords = zip(*self.model.data['projections'][self.layer].items())
        names = np.array(names)
        coords = np.stack(coords, axis=0)

        center_of_mass = np.average(coords, axis=0)
        coords -= center_of_mass  # center the data

        max_val = np.max(np.abs(coords))

        scale = (min(w/2, h/2)-(padding*2))/max_val
        coords = np.floor(coords*scale)

        # need to flip the y axis, because in tkinter the y-axis increases downwards
        max_y = np.max(coords[:, 1], axis=0)
        min_y = np.min(coords[:, 1], axis=0)
        coords[:, 1] = (max_y+min_y)-(coords[:, 1])
        coords += padding

        for name, (x, y) in zip(names, coords):
            x1, y1, x2, y2 = x-circle_radius, y-circle_radius, x+circle_radius, y+circle_radius
            real = self.model.data['prediction_results'][name]['real']
            cur_point = self.create_oval(x1, y1, x2, y2, fill=category10[real])
            self.tag_bind(cur_point, '<Button-1>', self.select_closure(name))
            self.tag_bind(cur_point, '<Double-Button-1>', self.add_closure(name))

    def select_closure(self, instance):
        return lambda event: self.model.select(instance)

    def add_closure(self, instance):
        return lambda event: self.model.add(instance)


class MainWindow:
    def __init__(self, master, model: DataModel):
        # TODO: create a dedicated window for scatter_canvas
        self.scatter_canvas = ScatterCanvas(tk.Toplevel(master),
                                            model,
                                            next(iter(model.data['projections'])),
                                            width=600,
                                            height=600)
        self.scatter_canvas.pack(expand=False)

        self.master = master
        self.model = model

        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        # self.master.grid_columnconfigure(0, weight=1)

        self.image_preview = ImageFrame(self.master, model, next(iter(model.data['images'])), width=280, height=280, image_scale=10)
        self.image_preview.grid(row=0, column=1, sticky='ne')

        self.button_panel = MenuPanel(self.master, self.model)
        self.button_panel.grid(row=0, column=0, sticky='nw')

        self.selector_window = ImageSelectorGallery(self.master, self.model)
        self.selector_window.grid(row=1, column=0, columnspan=2, sticky='nsew')

        self.model.observers.append(self)

    def notify(self, event):
        if isinstance(event, ModelEvent):
            if event.type == ModelEventType.SELECT:
                self.image_preview.update_canvas(event.data)



if __name__ == '__main__':
    # a json is needed containing the average activations for all digits in the first fully connected layer
    # can be created using the jupyter notebook
    with Path('./NN_data.json').open(mode='r') as file:
        network_data = json.loads(file.read())
    # print(activations)

    for key in network_data['images'].keys():
        network_data['images'][key] = np.array(network_data['images'][key])

    for layer in network_data['projections'].keys():
        for instance in network_data['projections'][layer].keys():
            network_data['projections'][layer][instance] = np.array(network_data['projections'][layer][instance])

    model = DataModel(network_data)

    # *model.selected, = (f'Digit {x}' for x in range(10))

    root = tk.Tk()
    image_data = network_data['images'][next(iter(network_data['images']))]
    # print(root.tk)
    # window.geometry("1550x450+300+300")

    app = MainWindow(root, model)

    root.mainloop()
