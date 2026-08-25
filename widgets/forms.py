
from .base import Widget
from .layouts import VerticalLayout, HorizontalLayout
from .label import Label
from .text_input import TextInput
from .button import Button
from renderer.colors import Palette, Color

class Form(VerticalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields = {}
        
    def add_field(self, name, widget):
        self.fields[name] = widget
        self.add_widget(widget)
        
    def get_data(self):
        data = {}
        for name, widget in self.fields.items():
            if hasattr(widget, 'text'):
                data[name] = widget.text
            elif hasattr(widget, 'checked'):
                data[name] = widget.checked
        return data
        
    def validate(self):
        return True # Implement logic

class FormField(VerticalLayout):
    def __init__(self, label="Field", input_widget=None, **kwargs):
        super().__init__(**kwargs)
        self.spacing = 5
        self.add_widget(Label(text=label, size=12, color=Palette.GRAY_700))
        if input_widget:
            self.add_widget(input_widget)
            self.input = input_widget

class Dropdown(Button):
    def __init__(self, items=[], **kwargs):
        super().__init__(**kwargs)
        self.items = items
        self.selected_index = -1
        self.text = "Select..."
        # On click show list logic

class ToggleButton(Button):
    def __init__(self, text_on="ON", text_off="OFF", **kwargs):
        super().__init__(**kwargs)
        self.text_on = text_on
        self.text_off = text_off
        self.checked = False
        self.text = text_off
        self.background_color = Palette.GRAY_400
        self.events.on_click.connect(self.toggle)
        
    def toggle(self):
        self.checked = not self.checked
        self.text = self.text_on if self.checked else self.text_off
        self.background_color = Palette.PRIMARY if self.checked else Palette.GRAY_400

class SegmentedControl(HorizontalLayout):
    def __init__(self, segments=[], **kwargs):
        super().__init__(**kwargs)
        self.segments = segments
        self.selected_index = 0
        self.spacing = 0
        
        for i, seg in enumerate(segments):
            btn = Button(text=seg, width=kwargs.get('width', 200)//len(segments))
            if i == 0:
                btn.background_color = Palette.PRIMARY
            else:
                btn.background_color = Palette.GRAY_300
            self.add_widget(btn)

class Stepper(HorizontalLayout):
    # Steps visualization
    pass

class Counter(HorizontalLayout):
    def __init__(self, value=0, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.spacing = 10
        
        self.lbl_val = Label(text=str(value), width=30, align="center")
        
        btn_minus = Button(text="-", width=30)
        btn_minus.events.on_click.connect(self.decrement)
        
        btn_plus = Button(text="+", width=30)
        btn_plus.events.on_click.connect(self.increment)
        
        self.add_widget(btn_minus)
        self.add_widget(self.lbl_val)
        self.add_widget(btn_plus)
        
    def increment(self):
        self.value += 1
        self.lbl_val.text = str(self.value)
        
    def decrement(self):
        self.value -= 1
        self.lbl_val.text = str(self.value)
