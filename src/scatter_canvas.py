import tkinter as tk

import numpy as np

from colormaps import category10


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