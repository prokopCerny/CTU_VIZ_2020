import tkinter as tk
from tkinter import ttk

from pathlib import Path
import json
import numpy as np

from datamodel import DataModel
from image_frame import ImageFrame
from image_gallery import ImageSelectorGallery
from layer_activations_window import LayerActivationsWindow
from utils import compute_needed_width_for_neurons


class MainWindow:
    def __init__(self, master, model: DataModel):
        # TODO: integrate selector_window into main window as a frame
        self.selector_window = ImageSelectorGallery(tk.Toplevel(master), model)
        self.selector_window.pack(fill=tk.BOTH, expand=True)
        # TODO: decide if to integrate image window into main frame
        self.image_window = ImageFrame(tk.Toplevel(master), model, next(iter(model.data['images'])), width=300, height=300, image_scale=10)
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
            new_window = LayerActivationsWindow(self.master, self.model, identifier)
            instances = self.model.data['activations'][identifier]

            new_window.geometry(f'{min(compute_needed_width_for_neurons(instances) + 20, 1250)}x400+300+300')
            new_window.title(f'{identifier} activations')
            self.activation_windows[identifier] = new_window


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
