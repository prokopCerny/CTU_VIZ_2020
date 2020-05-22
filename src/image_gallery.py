import tkinter as tk

from datamodel import ModelEvent, ModelEventType
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

        self.scroll_canvas_top = self.h_scrollbar_top = None
        self.scroll_canvas_bottom = self.h_scrollbar_bottom = None
        self.correct_label = self.incorrect_label = None

        self.show_numbers(0)

        self.model.observers.append(self)

    def notify(self, event):
        if isinstance(event, ModelEvent):
            if event.type == ModelEventType.SELECT:
                instance = event.data
                results = self.model.data['prediction_results'][instance]
                real, predicted = results['real'], results['pred']
                self.instance_label_var.set(f'{instance}: Real label: {real}, predicted: {predicted}')


    def button_callback_closure(self, digit:int):
        return lambda: self.show_numbers(digit)

    def show_numbers(self, digit: int):
        if self.scroll_canvas_top is not None:
            self.scroll_canvas_top.destroy()
        if self.h_scrollbar_top is not None:
            self.h_scrollbar_top.destroy()
        if self.scroll_canvas_bottom is not None:
            self.scroll_canvas_bottom.destroy()
        if self.h_scrollbar_bottom is not None:
            self.h_scrollbar_bottom.destroy()
        if self.correct_label is not None:
            self.correct_label.destroy()
        if self.incorrect_label is not None:
            self.incorrect_label.destroy()

        self.correct_label = tk.Label(self.bottom_frame, text=f'Correctly classified {digit}s', anchor='w')
        self.correct_label.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.scroll_canvas_top = tk.Canvas(self.bottom_frame, height=90)
        self.h_scrollbar_top = tk.Scrollbar(self.bottom_frame, command=self.scroll_canvas_top.xview, orient='horizontal')

        self.scroll_canvas_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.h_scrollbar_top.pack(side=tk.TOP, fill=tk.X)
        self.scroll_canvas_top.configure(xscrollcommand=self.h_scrollbar_top.set)

        self.top_canvas_frame = tk.Frame(self.scroll_canvas_top)
        self.top_canvas_window = self.scroll_canvas_top.create_window((0, 0), window=self.top_canvas_frame, anchor='nw')
        self.top_canvas_frame.bind('<Configure>',
                                   lambda event: self.scroll_canvas_top.configure(scrollregion=self.scroll_canvas_top.bbox('all')))


        self.incorrect_label = tk.Label(self.bottom_frame, text=f'Misclassified {digit}s', anchor='w')
        self.incorrect_label.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.scroll_canvas_bottom = tk.Canvas(self.bottom_frame, height=90)
        self.h_scrollbar_bottom = tk.Scrollbar(self.bottom_frame, command=self.scroll_canvas_bottom.xview, orient='horizontal')

        self.scroll_canvas_bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.h_scrollbar_bottom.pack(side=tk.TOP, fill=tk.X)
        self.scroll_canvas_bottom.configure(xscrollcommand=self.h_scrollbar_bottom.set)

        self.bottom_canvas_frame = tk.Frame(self.scroll_canvas_bottom)
        self.bottom_canvas_window = self.scroll_canvas_bottom.create_window((0, 0), window=self.bottom_canvas_frame, anchor='nw')
        self.bottom_canvas_frame.bind('<Configure>',
                                   lambda event: self.scroll_canvas_bottom.configure(scrollregion=self.scroll_canvas_bottom.bbox('all')))

        self.all_images = []
        correct_count, incorrect_count = 0, 0
        for instance in self.model.data['digit_to_instances'][str(digit)]:
            results = self.model.data['prediction_results'][instance]
            real, predicted = results['real'], results['pred']
            if real == predicted:
                correct_frame = self.top_canvas_frame
                correct_count += 1
                if correct_count > 50:
                    continue
            else:
                correct_frame = self.bottom_canvas_frame
                incorrect_count += 1
                if incorrect_count > 50:
                    continue
            cur_image = ImageFrame(correct_frame, self.model, instance, width=84, height=84, image_scale=3)
            self.all_images.append(cur_image)

        for imag in self.all_images:
            imag.set_binding('<Button-1>', self.single_click_image_closure(imag.instance))
            imag.set_binding('<Double-Button-1>', self.select_image_closure(imag.instance))
            imag.pack(side=tk.LEFT)


    def single_click_image_closure(self, instance):
        # setStringHandler = setStringVarEventHandlerClosure(self.instance_label_var, instance)
        def single_click_handler(event):
            # setStringHandler(event)
            self.model.select(instance)
        return single_click_handler

    def select_image_closure(self, instance):
        return lambda event: self.model.add(instance)