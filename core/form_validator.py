# core/form_validator.py
# Motor de Validación de Formularios para PyPhonOS
# Valida campos automáticamente con reglas predefinidas.

import re
from renderer.colors import Color, Palette


class ValidationRule:
    """Regla de validación individual."""

    def __init__(self, rule_type, value=None, message=None):
        self.rule_type = rule_type
        self.value = value
        self.message = message or self._default_message()

    def _default_message(self):
        messages = {
            "required": "Este campo es obligatorio",
            "email": "Ingresa un correo electrónico válido",
            "min_length": f"Mínimo {self.value} caracteres",
            "max_length": f"Máximo {self.value} caracteres",
            "pattern": "Formato no válido",
            "match": "Los campos no coinciden",
            "numeric": "Solo se permiten números",
            "alpha": "Solo se permiten letras",
            "alphanumeric": "Solo se permiten letras y números",
            "min_value": f"El valor mínimo es {self.value}",
            "max_value": f"El valor máximo es {self.value}",
            "url": "Ingresa una URL válida",
            "phone": "Ingresa un teléfono válido",
            "password_strength": "Contraseña débil (usa mayúsculas, números y símbolos)",
        }
        return messages.get(self.rule_type, "Campo no válido")

    def validate(self, value, all_values=None):
        """Retorna True si es válido, False si falla."""
        if self.rule_type == "required":
            return bool(value and str(value).strip())
        
        if not value and self.rule_type != "required":
            return True  # Si no es required y está vacío, pasa

        text = str(value)

        if self.rule_type == "email":
            return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text))
        elif self.rule_type == "min_length":
            return len(text) >= self.value
        elif self.rule_type == "max_length":
            return len(text) <= self.value
        elif self.rule_type == "pattern":
            return bool(re.match(self.value, text))
        elif self.rule_type == "match":
            return text == (all_values.get(self.value, '') if all_values else '')
        elif self.rule_type == "numeric":
            return text.isdigit()
        elif self.rule_type == "alpha":
            return text.replace(' ', '').isalpha()
        elif self.rule_type == "alphanumeric":
            return text.replace(' ', '').isalnum()
        elif self.rule_type == "min_value":
            try:
                return float(text) >= self.value
            except ValueError:
                return False
        elif self.rule_type == "max_value":
            try:
                return float(text) <= self.value
            except ValueError:
                return False
        elif self.rule_type == "url":
            return bool(re.match(r'https?://[^\s/$.?#].[^\s]*', text))
        elif self.rule_type == "phone":
            return bool(re.match(r'^\+?[\d\s-]{7,15}$', text))
        elif self.rule_type == "password_strength":
            has_upper = bool(re.search(r'[A-Z]', text))
            has_lower = bool(re.search(r'[a-z]', text))
            has_digit = bool(re.search(r'\d', text))
            has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', text))
            return len(text) >= 8 and has_upper and has_lower and has_digit and has_special
        
        return True


class FieldState:
    """Estado de validación de un campo."""
    def __init__(self):
        self.errors = []     # Lista de mensajes de error activos
        self.is_valid = True
        self.touched = False  # Si el usuario ya interactuó con el campo
        self.dirty = False    # Si el valor cambió desde el original


class FormValidator:
    """
    Motor de validación automática de formularios.

    Uso:
        form = FormValidator()

        # Registrar campos con reglas
        form.add_field("username", username_input, [
            ("required",),
            ("min_length", 3),
            ("alphanumeric",),
        ])
        form.add_field("email", email_input, [
            ("required",),
            ("email",),
        ])
        form.add_field("password", password_input, [
            ("required",),
            ("min_length", 8),
            ("password_strength",),
        ])
        form.add_field("confirm_password", confirm_input, [
            ("required",),
            ("match", "password", "Las contraseñas no coinciden"),
        ])

        # Validar todo al enviar
        if form.validate():
            print("Formulario válido!")
        else:
            print("Errores:", form.get_errors())

        # Validación en tiempo real (conectar a eventos)
        form.enable_live_validation()
    """

    def __init__(self):
        self._fields = {}      # nombre → {"widget": TextInput, "rules": [Rule], "state": FieldState}
        self._error_color = Palette.ERROR
        self._valid_color = Color(0, 150, 0)
        self._error_widgets = {}  # nombre → Label de error creado dinámicamente
        self.on_valid = None       # Callback cuando todo el formulario es válido
        self.on_invalid = None     # Callback cuando hay errores

    def add_field(self, name, widget, rules):
        """
        Registra un campo con sus reglas de validación.

        Args:
            name: Nombre único del campo (ej: "email")
            widget: El TextInput widget
            rules: Lista de tuplas (tipo, valor_opcional, mensaje_opcional)
                   Ej: [("required",), ("email",), ("min_length", 3, "Mínimo 3 chars")]
        """
        parsed_rules = []
        for rule_tuple in rules:
            rule_type = rule_tuple[0]
            value = rule_tuple[1] if len(rule_tuple) > 1 else None
            message = rule_tuple[2] if len(rule_tuple) > 2 else None
            parsed_rules.append(ValidationRule(rule_type, value, message))

        self._fields[name] = {
            "widget": widget,
            "rules": parsed_rules,
            "state": FieldState(),
        }

    def validate(self):
        """
        Valida todos los campos. Retorna True si todos pasan.
        Actualiza automáticamente los bordes de los TextInput a rojo/verde.
        """
        all_valid = True
        all_values = self._get_all_values()

        for name, field in self._fields.items():
            widget = field["widget"]
            rules = field["rules"]
            state = field["state"]
            value = self._get_widget_value(widget)

            state.errors = []
            state.is_valid = True
            state.touched = True

            for rule in rules:
                if not rule.validate(value, all_values):
                    state.errors.append(rule.message)
                    state.is_valid = False
                    all_valid = False

            self._update_widget_visual(name, state)

        if all_valid and callable(self.on_valid):
            self.on_valid()
        elif not all_valid and callable(self.on_invalid):
            self.on_invalid()

        return all_valid

    def validate_field(self, name):
        """Valida un campo individual."""
        if name not in self._fields:
            return True

        field = self._fields[name]
        widget = field["widget"]
        rules = field["rules"]
        state = field["state"]
        value = self._get_widget_value(widget)
        all_values = self._get_all_values()

        state.errors = []
        state.is_valid = True
        state.touched = True

        for rule in rules:
            if not rule.validate(value, all_values):
                state.errors.append(rule.message)
                state.is_valid = False

        self._update_widget_visual(name, state)
        return state.is_valid

    def enable_live_validation(self):
        """Conecta la validación en tiempo real a los eventos de cambio de cada campo."""
        for name, field in self._fields.items():
            widget = field["widget"]
            # Conectar al evento de cambio del TextInput
            if hasattr(widget, 'events') and hasattr(widget.events, 'on_change'):
                widget.events.on_change.connect(lambda n=name: self.validate_field(n))

    def get_errors(self):
        """Retorna un diccionario {nombre_campo: [errores]}."""
        return {
            name: field["state"].errors
            for name, field in self._fields.items()
            if field["state"].errors
        }

    def get_values(self):
        """Retorna un diccionario {nombre_campo: valor}."""
        return self._get_all_values()

    def is_valid(self):
        """Retorna True si todos los campos son válidos (sin re-validar)."""
        return all(f["state"].is_valid for f in self._fields.values())

    def reset(self):
        """Resetea todos los estados de validación y bordes."""
        for name, field in self._fields.items():
            field["state"] = FieldState()
            widget = field["widget"]
            if hasattr(widget, 'border_color'):
                widget.border_color = Palette.OUTLINE
            if hasattr(widget, 'border_width'):
                widget.border_width = 0

    def _get_widget_value(self, widget):
        """Extrae el texto de un TextInput."""
        if hasattr(widget, 'text'):
            return widget.text
        if hasattr(widget, 'value'):
            return widget.value
        return ""

    def _get_all_values(self):
        """Obtiene todos los valores actuales del formulario."""
        return {
            name: self._get_widget_value(field["widget"])
            for name, field in self._fields.items()
        }

    def _update_widget_visual(self, name, state):
        """Actualiza el borde y color del widget según su estado de validación."""
        field = self._fields[name]
        widget = field["widget"]

        if not state.touched:
            return

        if state.is_valid:
            if hasattr(widget, 'border_color'):
                widget.border_color = self._valid_color
            if hasattr(widget, 'border_width'):
                widget.border_width = 2
        else:
            if hasattr(widget, 'border_color'):
                widget.border_color = self._error_color
            if hasattr(widget, 'border_width'):
                widget.border_width = 2
