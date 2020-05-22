import tkinter as tk
from tkinter import ttk

import numpy as np

from datamodel import DataModel, ModelEvent, ModelEventType
from utils import compute_needed_width_for_neurons, Gradient
from neuron_activations_panel import NeuronActivationsPanel


class LayerActivationsWindow(tk.Toplevel):
    # TODO: CLEANUP CODE AND IMPROVE NAMING
    # TODO: make it inherit from Frame and not Toplevel
    def __init__(self, master, model: DataModel, layer_identifier: str):
        tk.Toplevel.__init__(self, master=master)
        self.model = model
        self.layer = layer_identifier
        self.selected_data = self.model.data['activations'][self.layer]

        self.topText = tk.StringVar()
        self.frame_for_top_label_alignment = tk.Frame(self)
        self.topTextLabel = tk.Label(self.frame_for_top_label_alignment, anchor='w', textvariable=self.topText)
        self.topText.set("Click on a neuron!")

        self.gradient_frame = tk.Frame(self.frame_for_top_label_alignment)
        self.gradient_frame.grid_columnconfigure(2, weight=1)
        self.minVar = tk.StringVar()
        self.maxVar = tk.StringVar()
        self.minVar.set("Min")
        self.maxVar.set("Max")
        self.minLabel = tk.Label(self.gradient_frame, anchor='w', textvariable=self.minVar)
        self.maxLabel = tk.Label(self.gradient_frame, anchor='e', textvariable=self.maxVar)
        self.gradient = Gradient(self.gradient_frame, height=20)
        self.sep = ttk.Separator(self.gradient_frame, orient=tk.VERTICAL)
        self.sep.grid(row=0, column=0, sticky='ns')
        self.minLabel.grid(row=0, column=1, sticky='w')
        self.gradient.grid(row=0, column=2, sticky='we')
        self.maxLabel.grid(row=0, column=3, sticky='e')

        self.frame_for_top_label_alignment.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.topTextLabel.pack(side=tk.LEFT)
        self.gradient_frame.pack(side=tk.RIGHT, fill=tk.X)

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
            self.minVar.set(f'{cur_min:.3f}')
            self.maxVar.set(f'{cur_max:.3f}')
            new_thing = NeuronActivationsPanel(self.frame, self.model, instance, self.topText, self.selected_data[instance], cur_min, cur_max)
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
                self.minVar.set(f'{cur_min:.3f}')
                self.maxVar.set(f'{cur_max:.3f}')
                for thing in self.neuron_activations.values():
                    thing.update_max_min(cur_max, cur_min)
            else:
                self.minVar.set(f'Min')
                self.maxVar.set(f'Max')

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
        for digit in self.model.selected_instances:
            self._add_instance(digit)