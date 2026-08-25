
from .dialogs import Dialog
from .base import Widget
from .label import Label
from .button import Button
from .layouts import VerticalLayout
from .progress_bar import ProgressBar
from renderer.colors import Palette, Color

class BiometricPrompt(Dialog):
    def __init__(self, title="Biometric Auth", subtitle="Log in using your credential", **kwargs):
        content = VerticalLayout(width=280, height=200, spacing=15)
        content.add_widget(Label(text=subtitle, size=14, color=Palette.GRAY_700))
        # Icon
        content.add_widget(Label(text="👆", size=40, width=280)) # Centered ideally
        content.add_widget(Label(text="Touch the sensor", size=12, color=Palette.GRAY_500))
        
        content.add_widget(Button(text="Cancel", width=280, height=40, background_color=Palette.TRANSPARENT, text_color=Palette.PRIMARY))
        
        super().__init__(title=title, content=content, **kwargs)

class FingerprintDialog(BiometricPrompt):
    pass

class SecureKeyboard(Widget):
    # Custom keyboard implementation
    # Placeholder for security logic (e.g. randomized keys)
    pass

class PasswordStrengthMeter(ProgressBar):
    def __init__(self, password="", **kwargs):
        super().__init__(**kwargs)
        self.update_strength(password)
        
    def update_strength(self, password):
        length = len(password)
        if length == 0:
            self.progress = 0
            self.color = Palette.GRAY_300
        elif length < 6:
            self.progress = 0.3
            self.color = Palette.ERROR
        elif length < 10:
            self.progress = 0.7
            self.color = Palette.WARNING
        else:
            self.progress = 1.0
            self.color = Palette.SUCCESS
