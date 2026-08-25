
from .base import Widget
from renderer.colors import Palette, Color
from .label import Label
from .button import Button
from .layouts import VerticalLayout, HorizontalLayout
import time

class Dialog(Widget):
    def __init__(self, title="Dialog", content=None, on_dismiss=None, **kwargs):
        super().__init__(**kwargs)
        self.background_color = Color(0, 0, 0, 150)  # Dimmed background
        self.visible = False
        self.on_dismiss = on_dismiss
        self.z_index = 1000  # Ensure it's on top

        # Container for the dialog box
        self.container = VerticalLayout(
            width=kwargs.get('width', 300) - 40,
            height=kwargs.get('height', 200),
            background_color=Palette.SURFACE,
            padding=20,
            spacing=10
        )
        self.container.border_radius = 12
        
        # Title
        self.title_label = Label(text=title, size=18, color=Palette.BLACK, width=self.container.width)
        self.container.add_widget(self.title_label)

        # Content
        if content:
            self.container.add_widget(content)
        
        # Center the container
        self.center_container()

    def center_container(self):
        if self.parent:
            self.width = self.parent.width
            self.height = self.parent.height
            self.container.x = (self.width - self.container.width) // 2
            self.container.y = (self.height - self.container.height) // 2

    def show(self):
        self.visible = True
        self.center_container()

    def dismiss(self):
        self.visible = False
        if self.on_dismiss:
            self.on_dismiss()

    def draw(self, canvas):
        if not self.visible:
            return
        # Draw dimmed background
        canvas.draw_rect(self.x, self.y, self.width, self.height, self.background_color, filled=True)
        # Draw container
        self.container.x = self.x + (self.width - self.container.width) // 2
        self.container.y = self.y + (self.height - self.container.height) // 2
        self.container.draw(canvas)

    def handle_event(self, event):
        if not self.visible:
            return False
        # Consume all events if visible (modal)
        if self.container.handle_event(event):
            return True
        
        # Dismiss on clicking outside if desired (optional)
        if event.get('type') == 'touch_down':
            return True 
        return False

class AlertDialog(Dialog):
    def __init__(self, title="Alert", message="Message", positive_text="OK", negative_text="Cancel", on_positive=None, on_negative=None, **kwargs):
        content = VerticalLayout(width=260, height=100, spacing=10)
        content.add_widget(Label(text=message, size=14, color=Palette.GRAY_700, width=260))
        
        buttons = HorizontalLayout(width=260, height=40, spacing=10)
        if negative_text:
            btn_neg = Button(text=negative_text, width=120, height=40, background_color=Palette.GRAY_200)
            btn_neg.events.on_click.connect(lambda: self._handle_negative(on_negative))
            buttons.add_widget(btn_neg)
        
        btn_pos = Button(text=positive_text, width=120, height=40, background_color=Palette.PRIMARY)
        btn_pos.events.on_click.connect(lambda: self._handle_positive(on_positive))
        buttons.add_widget(btn_pos)
        
        content.add_widget(buttons)
        super().__init__(title=title, content=content, **kwargs)

    def _handle_positive(self, callback):
        self.dismiss()
        if callback:
            callback()

    def _handle_negative(self, callback):
        self.dismiss()
        if callback:
            callback()

class BottomSheetDialog(Dialog):
    def draw(self, canvas):
        if not self.visible:
            return
        canvas.draw_rect(self.x, self.y, self.width, self.height, self.background_color, filled=True)
        
        # Align to bottom
        self.container.x = self.x
        self.container.y = self.y + self.height - self.container.height
        self.container.width = self.width
        self.container.border_radius = 0 # Reset or set top corners only if supported
        self.container.draw(canvas)

class DatePickerDialog(Dialog):
    def __init__(self, on_date_selected=None, **kwargs):
        # Placeholder for complex date picker logic
        content = VerticalLayout(width=280, height=300)
        content.add_widget(Label(text="Select Date", size=16))
        # ... Grid of days would go here ...
        btn = Button(text="Select Today", width=200, height=40)
        btn.events.on_click.connect(lambda: self._select("2023-10-27", on_date_selected))
        content.add_widget(btn)
        super().__init__(title="Date Picker", content=content, **kwargs)
    
    def _select(self, date, callback):
        self.dismiss()
        if callback:
            callback(date)

class TimePickerDialog(Dialog):
    def __init__(self, on_time_selected=None, **kwargs):
        content = VerticalLayout(width=280, height=200)
        content.add_widget(Label(text="Select Time", size=16))
        btn = Button(text="12:00 PM", width=200, height=40)
        btn.events.on_click.connect(lambda: self._select("12:00", on_time_selected))
        content.add_widget(btn)
        super().__init__(title="Time Picker", content=content, **kwargs)

    def _select(self, time_val, callback):
        self.dismiss()
        if callback:
            callback(time_val)

class Toast(Widget):
    def __init__(self, message, duration=2.0, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.duration = duration
        self.start_time = 0
        self.visible = False
        self.background_color = Color(50, 50, 50, 230)
        self.width = 200
        self.height = 40
        self.border_radius = 20

    def show(self):
        self.visible = True
        self.start_time = time.time()

    def draw(self, canvas):
        if not self.visible:
            return
        if time.time() - self.start_time > self.duration:
            self.visible = False
            return
            
        # Center bottom
        if self.parent:
            self.x = (self.parent.width - self.width) // 2
            self.y = self.parent.height - 80
            
        super().draw_background(canvas) # Assuming base has this or similar, otherwise manual
        canvas.draw_rect(self.x, self.y, self.width, self.height, self.background_color, filled=True, radius=self.border_radius)
        
        # Draw text centered
        # Simple text draw helper needed or use Label logic
        # For brevity reusing label logic if possible or manual
        pass # Text drawing logic implies using Label or Canvas text

class Snackbar(Widget):
    def __init__(self, message, action_text="UNDO", on_action=None, **kwargs):
        super().__init__(**kwargs)
        self.height = 50
        self.background_color = Palette.GRAY_900
        self.layout = HorizontalLayout(width=kwargs.get('width', 300), height=50, padding=10)
        self.layout.add_widget(Label(text=message, color=Palette.WHITE, width=200))
        if action_text:
            btn = Button(text=action_text, width=80, height=30, background_color=Palette.TRANSPARENT) # Transparent btn
            btn.text_color = Palette.PRIMARY # Assuming Button supports this
            if on_action:
                btn.events.on_click.connect(on_action)
            self.layout.add_widget(btn)
    
    def draw(self, canvas):
        # Draw background
        canvas.draw_rect(self.x, self.y, self.width, self.height, self.background_color, filled=True)
        self.layout.x = self.x
        self.layout.y = self.y
        self.layout.draw(canvas)

class PopupWindow(Dialog):
    # Similar to Dialog but anchored to a specific location
    pass

class Tooltip(Widget):
    # Small floating label
    pass
