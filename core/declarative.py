# core/declarative.py
# Motor de UI Declarativa para PyPhonOS
# Construye interfaces desde diccionarios Python o archivos JSON.

import json


# Registro de clases de widgets disponibles
_WIDGET_REGISTRY = {}


def register_widget(name, cls):
    """Registra una clase de widget para uso declarativo."""
    _WIDGET_REGISTRY[name] = cls


def _auto_register():
    """Registra automáticamente todos los widgets conocidos de PyPhonOS."""
    try:
        from widgets import (
            Widget, Label, Button, Switch, StatusBar, TextInput,
            Checkbox, RadioButton, Slider, ProgressBar, Spinner,
            Card, ScrollView, ListView, VerticalLayout, HorizontalLayout,
            LinearLayout, ConstraintLayout, RelativeLayout, FrameLayout,
            GridLayout, BottomNavigationView, NavigationBar, Toolbar,
            TabLayout, DrawerLayout
        )
        mapping = {
            "Widget": Widget, "Label": Label, "Button": Button,
            "Switch": Switch, "StatusBar": StatusBar, "TextInput": TextInput,
            "Checkbox": Checkbox, "RadioButton": RadioButton,
            "Slider": Slider, "ProgressBar": ProgressBar, "Spinner": Spinner,
            "Card": Card, "ScrollView": ScrollView, "ListView": ListView,
            "VerticalLayout": VerticalLayout, "HorizontalLayout": HorizontalLayout,
            "LinearLayout": LinearLayout, "ConstraintLayout": ConstraintLayout,
            "RelativeLayout": RelativeLayout, "FrameLayout": FrameLayout,
            "GridLayout": GridLayout, "BottomNavigationView": BottomNavigationView,
            "NavigationBar": NavigationBar, "Toolbar": Toolbar,
            "TabLayout": TabLayout, "DrawerLayout": DrawerLayout,
        }
        for name, cls in mapping.items():
            register_widget(name, cls)
    except ImportError as e:
        print(f"[Declarative] Advertencia: No se pudieron registrar algunos widgets: {e}")


def build_ui(spec, parent=None):
    """
    Construye un árbol de widgets a partir de un diccionario.

    Formato del diccionario:
    {
        "type": "VerticalLayout",
        "props": {"width": 360, "height": 800, "spacing": 16, "padding": 20},
        "children": [
            {"type": "Label", "props": {"text": "Hola Mundo", "size": 24}},
            {"type": "Button", "props": {"text": "OK", "width": 200, "height": 48}},
            {
                "type": "Card",
                "props": {"width": 320, "height": 120, "padding": 16},
                "children": [
                    {"type": "Label", "props": {"text": "Dentro de la Card"}}
                ]
            }
        ]
    }
    """
    # Auto-registrar widgets si aún no se hizo
    if not _WIDGET_REGISTRY:
        _auto_register()

    widget_type = spec.get("type")
    props = spec.get("props", {})
    children_specs = spec.get("children", [])
    widget_id = spec.get("id")
    events = spec.get("events", {})

    # Buscar la clase
    cls = _WIDGET_REGISTRY.get(widget_type)
    if cls is None:
        print(f"[Declarative] Widget tipo '{widget_type}' no encontrado. Usando Widget base.")
        from widgets.base import Widget
        cls = Widget

    # Crear instancia
    try:
        widget = cls(**props)
    except TypeError as e:
        print(f"[Declarative] Error creando {widget_type} con props {props}: {e}")
        widget = cls()

    # Asignar ID
    if widget_id:
        widget.id = widget_id

    # Construir hijos recursivamente
    for child_spec in children_specs:
        child = build_ui(child_spec, parent=widget)
        if hasattr(widget, 'add_widget'):
            widget.add_widget(child)
        else:
            widget.add_child(child)

    return widget


def build_from_json(json_path):
    """
    Carga un archivo JSON y construye la UI.

    Uso:
        root = build_from_json("ui/home_screen.json")
        app.add_widget(root)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    return build_ui(spec)


def build_from_string(json_string):
    """Construye UI desde un string JSON."""
    spec = json.loads(json_string)
    return build_ui(spec)


class DeclarativeScreen:
    """
    Pantalla que se construye desde un diccionario o JSON.
    Se integra con el Navigator.

    Uso:
        spec = {"type": "VerticalLayout", "children": [...]}
        screen = DeclarativeScreen("Home", spec)
        app.navigator.push(screen)
    """
    def __init__(self, name, spec=None, json_path=None):
        from core.navigator import Screen
        self._screen = type(name, (Screen,), {})()
        self._screen.name = name
        self._spec = spec
        self._json_path = json_path

    def build(self):
        if self._json_path:
            root = build_from_json(self._json_path)
        elif self._spec:
            root = build_ui(self._spec)
        else:
            return
        self._screen.add(root)

    def get_screen(self):
        self.build()
        self._screen._built = True
        return self._screen


def find_widget_by_id(root, widget_id):
    """
    Busca un widget por su ID en toda la jerarquía.
    Retorna el widget o None si no se encuentra.

    Uso:
        btn = find_widget_by_id(root, "btn_save")
        btn.events.on_click.connect(mi_funcion)
    """
    if getattr(root, 'id', None) == widget_id:
        return root
    for child in getattr(root, 'children', []):
        found = find_widget_by_id(child, widget_id)
        if found:
            return found
    return None
