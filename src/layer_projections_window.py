import tkinter as tk
from tkinter import ttk

from datamodel import DataModel
from colormaps import category10
from scatter_canvas import ScatterCanvas


class LayerProjectionsWindow(tk.Toplevel):
    def __init__(self, master, model: DataModel, scatter_width, scatter_height, **kw):
        super().__init__(master, **kw)
        self.model = model
        self.scatter_width = scatter_width
        self.scatter_height = scatter_height

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP)

        self.layerLabel = tk.Label(self.top_frame, text="Layer: ")
        self.layerLabel.grid(row=0, column=0, sticky='nw')

        layer_names = list(self.model.data['projections'].keys())
        self.selector = ttk.Combobox(self.top_frame, values=layer_names, state='readonly')
        self.selector.current(0)
        self.selector.bind('<<ComboboxSelected>>', self.update_canvas)
        print(self.selector.get())
        self.selector.grid(row=0, column=1, sticky='nw')

        self.legend = tk.Canvas(self, width=scatter_width, height=30)
        for i in range(2, 12):
            x = i*scatter_width/13
            c_y = 22
            c_r = 5
            self.legend.create_text(x, 8, text=f'{i-2}')
            self.legend.create_oval(x-c_r, c_y-c_r, x+c_r, c_y+c_r, fill=category10[i-2])
        self.legend.pack(side=tk.TOP)
        self.scatter_canvas = None
        self.update_canvas(None)



    def update_canvas(self, event):
        if self.scatter_canvas is not None:
            self.scatter_canvas.destroy()
        self.scatter_canvas = ScatterCanvas(self,
                                            self.model,
                                            self.selector.get(),
                                            width=self.scatter_width,
                                            height=self.scatter_height)
        self.scatter_canvas.pack(side=tk.BOTTOM)