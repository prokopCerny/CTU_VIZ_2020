import tkinter as tk

import numpy as np
from PIL import Image, ImageTk


class ImageFrame(tk.Frame):
    def __init__(self, master, model, instance, width=100, height=100, image_scale=1):
        super().__init__(master=master)
        self.w = width
        self.h = height
        self.instance = instance
        self.scale = image_scale
        self.model = model
        self.canvas = self.canvas_image = None
        self.update_canvas(instance)

    def update_canvas(self, instance):
        if self.canvas is not None:
            self.canvas.destroy()
        self.instance = instance
        image_data = self.model.data['images'][instance]
        im_h, im_w = image_data.shape
        imag = Image.fromarray(np.round(image_data*255)).resize(size=(im_h*self.scale, im_w*self.scale), resample=Image.NEAREST)
        img = ImageTk.PhotoImage(image=imag)
        self.canvas = tk.Canvas(self, width=self.w, height=self.h)
        self.canvas.pack()
        self.canvas.pic = img
        self.canvas_image = self.canvas.create_image(0,0, anchor="nw", image=img)

    def set_binding(self, binding: str, callback):
        if self.canvas:
            self.canvas.tag_bind(self.canvas_image, binding, callback)