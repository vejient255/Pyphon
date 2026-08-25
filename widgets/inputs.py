
from .base import Widget
from .text_input import TextInput
from .label import Label
from .layouts import HorizontalLayout, VerticalLayout
from .button import Button
from renderer.colors import Palette, Color
import sdl2

class SearchView(HorizontalLayout):
    def __init__(self, hint="Search...", on_query=None, **kwargs):
        super().__init__(**kwargs)
        self.height = 50
        self.spacing = 8
        self.padding = 8
        self.background_color = Palette.SURFACE
        self.border_radius = 25
        
        # Icon placeholder (Label for now)
        self.add_widget(Label(text="🔍", size=20, width=30))
        
        self.input = TextInput(placeholder=hint, width=kwargs.get('width', 200) - 80, height=34)
        # Remove border for seamless look
        self.input.border_width = 0 
        self.input.background_color = Palette.TRANSPARENT
        self.add_widget(self.input)
        
        self.on_query = on_query

class AutoCompleteTextView(VerticalLayout):
    def __init__(self, suggestions=[], **kwargs):
        super().__init__(**kwargs)
        self.input = TextInput(width=kwargs.get('width', 200), height=48)
        self.add_widget(self.input)
        
        self.suggestions_list = suggestions
        self.dropdown = VerticalLayout(width=kwargs.get('width', 200), height=0, background_color=Palette.SURFACE)
        self.dropdown.visible = False
        self.add_widget(self.dropdown)
        
        # Basic logic hook (pseudo-code as events need proper connecting)
        # self.input.events.on_text_change.connect(self.filter_suggestions)

    def filter_suggestions(self, text):
        # Implementation to filter and show dropdown
        pass

class PINEntry(HorizontalLayout):
    def __init__(self, length=4, **kwargs):
        super().__init__(spacing=10, **kwargs)
        self.digits = []
        for _ in range(length):
            ti = TextInput(width=40, height=50)
            ti.text_align = "center" # Assuming support
            self.add_widget(ti)
            self.digits.append(ti)

class RatingBar(HorizontalLayout):
    def __init__(self, max_stars=5, rating=0, **kwargs):
        super().__init__(spacing=4, **kwargs)
        self.max_stars = max_stars
        self.rating = rating
        self.stars = []
        for i in range(max_stars):
            s = Label(text="★" if i < rating else "☆", size=24, color=Palette.WARNING)
            # Add click event to set rating
            self.add_widget(s)
            self.stars.append(s)

class RangeSlider(Widget):
    def __init__(self, min_val=0, max_val=100, **kwargs):
        super().__init__(**kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.start_val = min_val
        self.end_val = max_val
        # Draw logic for two thumbs
    
    def draw(self, canvas):
        # Track
        canvas.draw_rect(self.x, self.y + self.height//2 - 2, self.width, 4, Palette.GRAY_300, filled=True)
        # Selected range
        # Thumbs
        pass

class ColorPicker(Widget):
    # Complex widget, placeholder implementation
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_color = Palette.PRIMARY
        
    def draw(self, canvas):
        # Draw gradient rect
        pass

class NumberPicker(VerticalLayout):
    def __init__(self, min_val=0, max_val=10, **kwargs):
        super().__init__(**kwargs)
        self.value = min_val
        self.label = Label(text=str(self.value))
        
        btn_up = Button(text="▲", height=30)
        btn_down = Button(text="▼", height=30)
        
        self.add_widget(btn_up)
        self.add_widget(self.label)
        self.add_widget(btn_down)

class SignaturePad(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = []
        self.is_drawing = False
        
    def handle_event(self, event):
        if event['type'] == 'touch_down':
            self.is_drawing = True
            self.points.append([]) # New stroke
        elif event['type'] == 'touch_up':
            self.is_drawing = False
        elif event['type'] == 'touch_move' and self.is_drawing:
            if self.points:
                self.points[-1].append((event['x'], event['y']))
        return True # Consume
        
    def draw(self, canvas):
        super().draw(canvas) # Background
        # Draw lines
        for stroke in self.points:
            if len(stroke) > 1:
                for i in range(len(stroke) - 1):
                    canvas.draw_line(stroke[i][0], stroke[i][1], stroke[i+1][0], stroke[i+1][1], Palette.BLACK)
