import tkinter as tk

from colormaps import viridis


def RGBtoHex(vals, rgbtype=1):
    """Converts RGB values in a variety of formats to Hex values.

       :param  vals:     An RGB/RGBA tuple
       :param  rgbtype:  Valid values are:
                            1 - Inputs are in the range 0 to 1
                          256 - Inputs are in the range 0 to 255

       :return A hex string in the form '#RRGGBB' or '#RRGGBBAA'
  """
    # Stolen from stackoverflow
    # TODO: rewrite shorter
    if len(vals) != 3 and len(vals) != 4:
        raise Exception("RGB or RGBA inputs to RGBtoHex must have three or four elements!")
    if rgbtype != 1 and rgbtype != 256:
        raise Exception("rgbtype must be 1 or 256!")

    #Convert from 0-1 RGB/RGBA to 0-255 RGB/RGBA
    if rgbtype == 1:
        if not all(0 <= x <= 1 for x in vals):
            raise Exception("RGB1 values are not in range 0-1")
        vals = [255 * x for x in vals]

    #Ensure values are rounded integers, convert to hex, and concatenate
    return '#' + ''.join([f'{int(round(x)):02X}' for x in vals])


def setStringVarEventHandlerClosure(stringVariable: tk.StringVar, text: str):
    def setStringVarEventHandler(event):
        # print(f'Clicked at {event.x}, {event.y}')
        stringVariable.set(text)
        #print(event.widget.itemconfig(event.widget.find_withtag('current'), fill='green'))
    return setStringVarEventHandler


def find_smallest_missing(lst):
    if lst:
        if lst[0] != 0:
            return 0
        else:
            for i in range(len(lst)-1):
                if lst[i+1] - lst[i] > 1:
                    return lst[i] + 1
            return lst[-1]+1
    else:
        return 0


def compute_needed_width_for_neurons(layer_data):
    first_instance_key = next(iter(layer_data))
    neuron_count = len(layer_data[first_instance_key])
    return 6+5+80+neuron_count*23


def get_average_digit_instance_name(digit: int):
    return f'Average {digit}'


class Gradient(tk.Canvas):
    def __init__(self, master, colormap=viridis, **kw):
        super().__init__(master, **kw)
        self.cmap = colormap
        self.bind('<Configure>', self.draw_gradient)

    def draw_gradient(self, event):
        self.delete("grad")
        w, h = self.winfo_width(), self.winfo_height()
        if w > 1:
            for i in range(w):
                color = self.cmap((i*w)/(w*(w-1)))
                self.create_line(i, 0, i, h, tags=("grad",), fill=RGBtoHex(color))