import tkinter as tk

from colormaps import viridis
from utils import RGBtoHex, setStringVarEventHandlerClosure


class NeuronActivationsPanel(tk.Frame):
    def __init__(self, master, model, instance, stringVariable, neuron_activations, min_act, max_act, colormap=viridis):
        super().__init__(master=master, height=30)
        self.cmap = colormap
        self.label = tk.Label(self, text=instance, anchor='w', width=8)
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