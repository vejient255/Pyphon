
from .base import Widget
from .label import Label
from .layouts import VerticalLayout
from renderer.colors import Palette, Color

class ChatBubble(Widget):
    def __init__(self, message="Hello", is_me=True, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.is_me = is_me
        self.background_color = Palette.PRIMARY if is_me else Palette.GRAY_300
        self.text_color = Palette.WHITE if is_me else Palette.BLACK
        self.border_radius = 12
        
    def draw(self, canvas):
        # Bubble shape
        canvas.draw_rect(self.x, self.y, self.width, self.height, self.background_color, filled=True, radius=self.border_radius)
        # Text
        canvas.draw_text(self.message, self.x + 10, self.y + 10, self.text_color)

class MessageView(VerticalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(ChatBubble(message="Hi there!", is_me=False, width=200, height=40))
        self.add_widget(ChatBubble(message="Hello!", is_me=True, width=200, height=40))

class NotificationCenter(VerticalLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Notifications", size=16))
        # List of notifs

class InboxView(VerticalLayout):
    pass
