# PyPhonOS - signals.py


class Signal:
    def __init__(self):
        self._slots = []

    def connect(self, slot):
        """Conecta una función (slot) a esta señal."""
        if slot not in self._slots:
            self._slots.append(slot)

    def emit(self, *args, **kwargs):
        """Ejecuta todas las funciones conectadas."""
        for slot in self._slots:
            slot(*args, **kwargs)