import tkinter as tk

from utils import setStringVarEventHandlerClosure
from image_frame import ImageFrame


class ImageSelectorGallery(tk.Frame):
    def __init__(self, master, model):
        super().__init__(master=master)
        self.model = model
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.instance_label_var = tk.StringVar()
        self.instance_label_var.set("Click on an image to see details, doubleclick to select")
        self.instance_label = tk.Label(self.top_frame, textvariable=self.instance_label_var)
        self.instance_label.pack(side=tk.RIGHT)

        self.digit_buttons = [tk.Button(self.top_frame,
                                        text=f'{digit}',
                                        command=self.button_callback_closure(digit))
                              for digit in range(10)]
        for button in self.digit_buttons:
            button.pack(side=tk.LEFT)
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

        self.imags = [ImageFrame(self.canvas_frame, self.model, instance, width=84, height=84, image_scale=3)
                      for idx, instance
                      in enumerate(self.model.data['digit_to_instances'][str(digit)])
                      if idx < 50]
        for imag in self.imags:
            imag.set_binding('<Button-1>', setStringVarEventHandlerClosure(self.instance_label_var, imag.instance))
            imag.set_binding('<Double-Button-1>', self.select_image_closure(imag.instance))
            imag.pack(side=tk.LEFT)

    def select_image_closure(self, instance):
        return lambda event: self.model.select(instance)