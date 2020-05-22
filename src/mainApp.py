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


class MainWindow:
    def __init__(self, master, model: DataModel):
        # TODO: integrate selector_window into main window as a frame
        # TODO: decide if to integrate image window into main frame
        # self.image_window = ImageFrame(tk.Toplevel(master), model, next(iter(model.data['images'])), width=300, height=300, image_scale=10)
        # self.image_window.pack()

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

    model = DataModel(network_data)

    # *model.selected, = (f'Digit {x}' for x in range(10))

    root = tk.Tk()
    image_data = network_data['images'][next(iter(network_data['images']))]
    # print(root.tk)
    # window.geometry("1550x450+300+300")

    app = MainWindow(root, model)

    root.mainloop()
