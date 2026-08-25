# core/animation.py
# Motor de Animaciones para PyPhonOS - Material Motion
# Implementa interpolación de propiedades con múltiples curvas de easing.

import time
import math


# ─────────────────────────────────────────────
# 1. CURVAS DE EASING (Material Motion)
# ─────────────────────────────────────────────

class Easing:
    """Colección de funciones de interpolación (t en [0.0, 1.0] → valor en [0.0, 1.0])."""

    @staticmethod
    def linear(t):
        return t

    @staticmethod
    def ease_in(t):
        return t * t

    @staticmethod
    def ease_out(t):
        return t * (2 - t)

    @staticmethod
    def ease_in_out(t):
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

    @staticmethod
    def bounce(t):
        """Rebota al final (estilo Android "Overshoot")."""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

    @staticmethod
    def spring(t):
        """Efecto de resorte suave."""
        return math.sin(t * math.pi * (0.2 + 2.5 * t * t * t)) * ((1 - t) ** 2.2) + t

    @staticmethod
    def elastic(t):
        """Elástico exagerado."""
        if t == 0 or t == 1:
            return t
        return -(2 ** (10 * t - 10)) * math.sin((t * 10 - 10.75) * (2 * math.pi) / 3)

    @staticmethod
    def overshoot(t):
        """Pasa del valor final y regresa (Material Emphasized Decelerate)."""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

    @staticmethod
    def decelerate(t):
        """Desaceleración suave (entrada natural)."""
        return 1 - (1 - t) ** 2

    @staticmethod
    def anticipate(t):
        """Retrocede un poco antes de avanzar (efecto de arranque)."""
        return t * t * ((2.70158 + 1) * t - 2.70158)

    FUNCTIONS = {
        "linear":       linear.__func__,
        "ease_in":      ease_in.__func__,
        "ease_out":     ease_out.__func__,
        "ease_in_out":  ease_in_out.__func__,
        "bounce":       bounce.__func__,
        "spring":       spring.__func__,
        "elastic":      elastic.__func__,
        "overshoot":    overshoot.__func__,
        "decelerate":   decelerate.__func__,
        "anticipate":   anticipate.__func__,
    }

    @classmethod
    def get(cls, name: str):
        fn = cls.FUNCTIONS.get(name)
        if fn is None:
            raise ValueError(f"Easing '{name}' desconocido. Opciones: {list(cls.FUNCTIONS.keys())}")
        return fn


# ─────────────────────────────────────────────
# 2. TWEEN: UNA ANIMACIÓN DE UNA PROPIEDAD
# ─────────────────────────────────────────────

class Tween:
    """
    Anima UNA propiedad de UN objeto de `start` a `end` en `duration` segundos.
    """
    def __init__(self, target, prop, start, end, duration, easing="ease_out",
                 delay=0.0, on_complete=None, auto_reverse=False, repeat=0):
        self.target = target
        self.prop = prop
        self.start = start
        self.end = end
        self.duration = duration
        self.easing_fn = Easing.get(easing)
        self.delay = delay
        self.on_complete = on_complete
        self.auto_reverse = auto_reverse
        self.repeat = repeat  # 0 = sin repetición, -1 = infinito

        self._start_time = None
        self._is_reversed = False
        self._repeat_count = 0
        self.finished = False

    def start_now(self):
        self._start_time = time.time() + self.delay

    def update(self) -> bool:
        """Devuelve True si la animación sigue activa, False si terminó."""
        if self.finished:
            return False

        now = time.time()
        if self._start_time is None or now < self._start_time:
            return True  # En delay, sigue activa

        elapsed = now - self._start_time
        t = min(elapsed / self.duration, 1.0)

        # Aplicar easing
        eased_t = self.easing_fn(t)

        # Calcular valor actual
        if self._is_reversed:
            value = self.end + (self.start - self.end) * eased_t
        else:
            value = self.start + (self.end - self.start) * eased_t

        # Aplicar valor al objeto
        try:
            setattr(self.target, self.prop, type(self.start)(value))
        except (TypeError, ValueError):
            setattr(self.target, self.prop, value)

        # ¿Terminó?
        if t >= 1.0:
            if self.auto_reverse and not self._is_reversed:
                self._is_reversed = True
                self._start_time = time.time()
                return True

            self._repeat_count += 1
            if self.repeat == -1 or self._repeat_count <= self.repeat:
                # Reiniciar
                self._is_reversed = False
                self._start_time = time.time()
                return True

            # Asegurar valor final exacto
            final = self.start if (self._is_reversed and self.auto_reverse) else self.end
            try:
                setattr(self.target, self.prop, type(self.start)(final))
            except:
                setattr(self.target, self.prop, final)

            self.finished = True
            if callable(self.on_complete):
                self.on_complete()
            return False

        return True


# ─────────────────────────────────────────────
# 3. ANIMATION MANAGER: CONTROLADOR GLOBAL
# ─────────────────────────────────────────────

class AnimationManager:
    """
    Gestiona todas las animaciones activas del sistema.
    Se integra en el bucle principal de MobileApp.

    Uso:
        from core.animation import AnimationManager
        anim = AnimationManager()   # Se asigna en MobileApp en app.py

        # Animar propiedad
        anim.tween(mi_widget, 'y', from_val=0, to_val=200, duration=0.5, easing='bounce')

        # Fade in de un widget
        anim.fade_in(mi_widget, duration=0.4)

        # Llamar en cada frame
        anim.update()
    """

    # Instancia singleton global
    INSTANCE = None

    def __init__(self):
        self._tweens: list[Tween] = []
        AnimationManager.INSTANCE = self

    def tween(self, target, prop, to_val, from_val=None, duration=0.3,
              easing="ease_out", delay=0.0, on_complete=None,
              auto_reverse=False, repeat=0) -> Tween:
        """
        Anima una propiedad de un widget.

        Args:
            target: El objeto a animar (cualquier widget o clase con atributos).
            prop: Nombre de la propiedad como string (ej. 'x', 'y', 'width', 'height').
            to_val: Valor final deseado.
            from_val: Valor inicial (si es None, usa el valor actual).
            duration: Duración en segundos.
            easing: Curva de animación. Opciones: 'linear', 'ease_out', 'bounce', 'spring', etc.
            delay: Segundos de espera antes de iniciar.
            on_complete: Callback al terminar.
            auto_reverse: Si True, la animación regresa al valor inicial.
            repeat: Número de repeticiones (0 = ninguna, -1 = infinito).
        """
        start = from_val if from_val is not None else getattr(target, prop, 0)
        t = Tween(target, prop, start, to_val, duration, easing, delay, on_complete, auto_reverse, repeat)
        t.start_now()
        self._tweens.append(t)
        return t

    def fade_in(self, widget, duration=0.3, delay=0.0, on_complete=None):
        """Aparece el widget con un fade (alpha de 0 a 255)."""
        if hasattr(widget, 'background_color') and widget.background_color:
            widget.background_color.a = 0
            self.tween(widget.background_color, 'a', 255, 0, duration, 'ease_out', delay, on_complete)
        widget.visible = True

    def fade_out(self, widget, duration=0.3, delay=0.0, on_complete=None):
        """Desvanece el widget hasta hacerlo invisible."""
        def _hide():
            widget.visible = False
            if callable(on_complete):
                on_complete()
        if hasattr(widget, 'background_color') and widget.background_color:
            self.tween(widget.background_color, 'a', 0, widget.background_color.a,
                       duration, 'ease_in', delay, _hide)

    def slide_in(self, widget, from_x=None, from_y=None, duration=0.35, easing="decelerate", delay=0.0):
        """Desliza el widget desde una posición a su posición actual."""
        if from_x is not None:
            target_x = widget.x
            widget.x = from_x
            self.tween(widget, 'x', target_x, from_x, duration, easing, delay)
        if from_y is not None:
            target_y = widget.y
            widget.y = from_y
            self.tween(widget, 'y', target_y, from_y, duration, easing, delay)

    def slide_out(self, widget, to_x=None, to_y=None, duration=0.3, easing="ease_in", delay=0.0, on_complete=None):
        """Desliza el widget hacia una posición de salida."""
        if to_x is not None:
            self.tween(widget, 'x', to_x, widget.x, duration, easing, delay, on_complete)
        if to_y is not None:
            self.tween(widget, 'y', to_y, widget.y, duration, easing, delay, on_complete)

    def scale(self, widget, to_width=None, to_height=None, duration=0.25, easing="spring", delay=0.0):
        """Escala el widget a un nuevo tamaño."""
        if to_width is not None:
            self.tween(widget, 'width', to_width, widget.width, duration, easing, delay)
        if to_height is not None:
            self.tween(widget, 'height', to_height, widget.height, duration, easing, delay)

    def pulse(self, widget, scale_factor=1.1, duration=0.15):
        """Efecto de pulso (crece y regresa). Ideal para feedback de botón."""
        orig_w = widget.width
        orig_h = widget.height
        peak_w = int(orig_w * scale_factor)
        peak_h = int(orig_h * scale_factor)
        
        offset_x = (peak_w - orig_w) // 2
        offset_y = (peak_h - orig_h) // 2

        def _shrink():
            self.tween(widget, 'width',  orig_w,   peak_w, duration, 'ease_in')
            self.tween(widget, 'height', orig_h,   peak_h, duration, 'ease_in')
            self.tween(widget, 'x',      widget.x, widget.x - offset_x, duration, 'ease_in')
            self.tween(widget, 'y',      widget.y, widget.y - offset_y, duration, 'ease_in')

        self.tween(widget, 'width',  peak_w,           orig_w, duration, 'ease_out', on_complete=_shrink)
        self.tween(widget, 'height', peak_h,           orig_h, duration, 'ease_out')
        self.tween(widget, 'x',      widget.x - offset_x, widget.x, duration, 'ease_out')
        self.tween(widget, 'y',      widget.y - offset_y, widget.y, duration, 'ease_out')

    def stagger(self, widgets, prop, to_val, from_val=None, duration=0.3,
                easing="ease_out", stagger_delay=0.06):
        """
        Anima una lista de widgets con un pequeño retraso entre cada uno.
        Ideal para efectos de entrada de listas (Material List Animation).
        """
        for i, widget in enumerate(widgets):
            self.tween(widget, prop, to_val, from_val,
                       duration, easing, delay=i * stagger_delay)

    def cancel(self, target=None, prop=None):
        """Cancela animaciones de un target/propiedad específicos."""
        self._tweens = [
            t for t in self._tweens
            if not (
                (target is None or t.target is target) and
                (prop is None or t.prop == prop)
            )
        ]

    def update(self):
        """Avanza todas las animaciones activas. Llamar en cada frame del loop principal."""
        self._tweens = [t for t in self._tweens if t.update()]

    @property
    def is_animating(self) -> bool:
        return len(self._tweens) > 0
